package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	salesparser "github.com/katy248/sales-parser"
)

func main() {

	flag.Parse()

	url := flag.Arg(0)

	offers, err := salesparser.Parse(url)
	if err != nil {
		fmt.Fprintln(os.Stderr, "Failed parse by url:", err)
		os.Exit(1)
	}

	res, _ := json.Marshal(offers)
	fmt.Println(string(res))

}
