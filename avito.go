package salesparser

import (
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/anaskhan96/soup"
)

func ParseAvito(u *url.URL) ([]Offer, error) {
	parser, err := getGoop(u)
	if err != nil {
		return nil, fmt.Errorf("failed create parser: %s", err)
	}
	offers := []Offer{}

	nodes := parser.FindAll("div", "data-marker", "item")
	for _, n := range nodes {

		o := Offer{}

		price, err := strconv.Atoi(n.Find("meta", "itemprop", "price").Attrs()["content"])
		if err != nil {
			continue
		}
		o.Price = float32(price)

		o.URL = u.Host + n.Find("a", "itemprop", "url").Attrs()["href"]

		offers = append(offers, o)
	}
	return offers, nil
}

func getGoop(u *url.URL) (*soup.Root, error) {
	data, err := getPageData(u)
	if err != nil {
		return nil, fmt.Errorf("failed get page data: %s", err)
	}

	root := soup.HTMLParse(string(data))

	return &root, nil
}

func getPageData(u *url.URL) ([]byte, error) {
	if data, ok := getCacheData(u); ok {
		fmt.Fprintln(os.Stderr, "[DEBUG] Data cached")
		return data, nil
	} else {
		fmt.Fprintf(os.Stderr, "[DEBUG] Data not cached\n")
	}

	data, err := getDataFromWeb(u)
	if err != nil {
		return nil, err
	}
	return data, nil
}

func getDataFromWeb(u *url.URL) ([]byte, error) {
	fmt.Fprintf(os.Stderr, "[DEBUG] Get page %q from web\n", u.String())
	resp, err := http.Get(u.String())
	if err != nil {
		return nil, fmt.Errorf("failed get page %q from web: %s", u.String(), err)
	}
	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed read response body: %s", err)
	}
	err = os.WriteFile(
		getCacheFile(u),
		data,
		0644,
	)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed write cache for url %q: %s", u.String(), err)
	}
	return data, nil
}

func getCacheData(u *url.URL) (data []byte, ok bool) {
	cacheFile := getCacheFile(u)

	cacheFileInfo, err := os.Stat(cacheFile)
	if err != nil {
		fmt.Fprintln(os.Stderr, "Can't get file info:", err)
		return nil, false
	}
	if cacheFileInfo.IsDir() {
		fmt.Fprintln(os.Stderr, "Cache file is a directory")
		return nil, false
	}

	if time.Until(cacheFileInfo.ModTime()) > CacheTime {
		return nil, false
	}

	data, err = os.ReadFile(cacheFile)
	if err != nil {
		fmt.Fprintln(os.Stderr, "Failed read cache file:", err)
		return nil, false
	}

	return data, true
}

func getCacheFile(u *url.URL) string {
	return getCacheDir() + "/" +
		strings.ReplaceAll(
			strings.Replace(u.String(), "https://", "", 1), "/", "_")
}

const CacheTime = time.Hour

func getCacheDir() string {
	dir, err := os.UserCacheDir()
	if err != nil {
		fmt.Fprintln(os.Stderr, "There is no cache dir")
		os.Exit(1)
	}
	cacheDir := dir + "/sales-parser"
	if err := os.Mkdir(cacheDir, 0755); err != nil && !os.IsExist(err) {
		fmt.Fprintf(os.Stderr, "Failed create cache dir (%q): %s\n", cacheDir, err)
		os.Exit(1)
	}
	return cacheDir
}
