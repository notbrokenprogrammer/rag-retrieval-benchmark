package main

type Document struct {
	Text   string
	Name   string
	Length int
}

type SearchResult struct {
	Document *Document
	Score    float64
}
