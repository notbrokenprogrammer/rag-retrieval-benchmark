package main

import (
	"bufio"
	"fmt"
	"math"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	log "github.com/sirupsen/logrus"
)

func calculationIdf(df int, n int) float64 {
	return math.Log(1 + (float64(n)-float64(df)+0.5)/(float64(df)+0.5))
}

func bm25TermScore(idf float64, tf int, avgdl float64, d int) float64 {
	const k1 = 1.5 // Насколько потворения слов влияет на результат
	const b = 0.75 // Характерезиует насколько учитывается длина файла
	return idf * (float64(tf) * (k1 + 1) / (float64(tf) + k1*(1-b+b*(float64(d)/avgdl))))
}

func main() {
	var Documents []*Document
	dir, err := os.ReadDir("data/documents")
	if err != nil {
		log.Error("Ошибка открытия директории")
		return
	}

	const basePath = "data/preparsing"
	for _, file := range dir {
		if file.IsDir() {
			continue
		}
		Doc := &Document{}

		Doc.Name = file.Name()
		fileName := filepath.Join(basePath, file.Name())

		textDoc, err := os.ReadFile(fileName)
		if err != nil {
			log.Error("Ошибка чтения файла")
			continue
		}
		Doc.Text = string(textDoc)

		Documents = append(Documents, Doc)

	}

	reader := bufio.NewReader(os.Stdin)
	fmt.Println("Пришлите текст")
	text, err := reader.ReadString('\n')
	if err != nil {
		log.Error("Ошибка чтения строки")
	}
	text = strings.TrimSpace(text)
	cmd := exec.Command("python3", "convert.py", text)
	output, err := cmd.Output() // Получение вывода от python
	if err != nil {
		log.Error("Ошибка вывода команды")
	}

	textArr := strings.Fields(string(output))

	tf := make(map[string]int)
	df := make(map[string]int)

	for _, x := range textArr {
		tf[x] = 0
	}
	var n int
	var countSum int

	for _, d := range Documents {
		n++
		text := strings.Fields(d.Text)
		for _, x := range text {
			d.Length++ // Подсчёт слов
			_, ok := tf[x]
			if ok {
				tf[x]++ // Сколько раз встречается
			}
		}
		for w, x := range tf { // Во скольких файлах встречается
			if x > 0 {
				df[w]++
			}
		}

		countSum += d.Length
		for k := range tf { // Очистка для дальнейшего прохода
			tf[k] = 0
		}
	}
	idf := make(map[string]float64)

	for val, x := range df {
		idf[val] = calculationIdf(x, n)
	}
	avgdl := float64(countSum) / float64(n)

	var results []SearchResult
	for _, d := range Documents {
		tf := make(map[string]int)
		for _, w := range textArr {
			tf[w] = 0
		}

		for _, w := range strings.Fields(d.Text) {
			_, ok := tf[w]
			if ok {
				tf[w]++
			}
		}

		score := 0.0

		for w, i := range tf {
			if i == 0 {
				continue
			}

			score += bm25TermScore(idf[w], i, avgdl, d.Length)
		}

		results = append(results, SearchResult{
			Document: d,
			Score:    score,
		})

	}
	for _, x := range results {
		fmt.Println(x.Document.Name)
		fmt.Println(x.Score)
	}
}
