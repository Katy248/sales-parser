package salesparser

import (
	"fmt"
	"net/url"
)

type ParserFunc func(*url.URL) ([]Offer, error)

type Offer struct {
	URL   string  `json:"url"`
	Price float32 `json:"price"`
}

var parsers = map[string]ParserFunc{
	"avito.ru":     ParseAvito,
	"www.avito.ru": ParseAvito,
}

func Parse(u string) ([]Offer, error) {
	parsedUrl, err := asURL(u)
	if err != nil {
		return nil, fmt.Errorf("failed parse URL %q: %s", u, err)
	}

	parser, ok := parsers[parsedUrl.Host]
	if !ok {
		return nil, fmt.Errorf("parsing of %q URLs isn't supported yet", parsedUrl.Host)
	}

	return parser(parsedUrl)
}

func asURL(u string) (*url.URL, error) {
	parsed, err := url.Parse(u)
	if err != nil {
		return nil, fmt.Errorf("bad url: %s", err)
	}
	return parsed, nil
}
