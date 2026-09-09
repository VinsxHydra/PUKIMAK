package main

import (
        "bufio"
        "fmt"
        "log"
        "os"
        "strings"
)

func writeResult(filename, result string) {
        f, err := os.OpenFile("result14/"+filename, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
        if err != nil {
                log.Println("Gagal buka file", filename)
                return
        }
        defer f.Close()
        f.WriteString(result + "\n")
}

func extractLine(line string) {
        line = strings.TrimSpace(line)
        if line == "" || strings.HasPrefix(line, "#") {
                return
        }

        if strings.Contains(line, "wp-login.php") && strings.Count(line, ":") >= 2 {
                parts := strings.SplitN(line, ":", 3)
                result := fmt.Sprintf("%s#%s@%s", parts[0], parts[1], parts[2])
                writeResult("wp.txt", result)
                return
        }

        if strings.Contains(line, ":2083") && strings.Count(line, ":") >= 4 {
        parts := strings.SplitN(line, ":", 5)
        result := fmt.Sprintf("https://%s:2083:%s:%s", parts[1], parts[3], parts[4])
        writeResult("cpanel.txt", result)
        return
        }
        if strings.Contains(line, ":2082") && strings.Count(line, ":") >= 4 {
        parts := strings.SplitN(line, ":", 5)
        result := fmt.Sprintf("https://%s:2082:%s:%s", parts[1], parts[3], parts[4])
        writeResult("cpanel.txt", result)
        return
        }

        if strings.Contains(line, ":2087") && strings.Count(line, ":") >= 4 {
                parts := strings.SplitN(line, ":", 5)
                result := fmt.Sprintf("https://%s:2087|%s|%s", parts[1], parts[3], parts[4])
                writeResult("whm.txt", result)
                return
        }

        if strings.Contains(line, "ftp.") && strings.Count(line, ":") >= 2 {
                parts := strings.SplitN(line, ":", 3)
                result := fmt.Sprintf("%s|%s|%s", parts[0], parts[1], parts[2])
                writeResult("ftp.txt", result)
                return
        }

        if strings.Contains(line, "/administrator/index.php") && strings.Count(line, ":") >= 2 {
                parts := strings.SplitN(line, ":", 3)
                result := fmt.Sprintf("%s|%s|%s", parts[0], parts[1], parts[2])
                writeResult("joomla.txt", result)
                return
        }

        if strings.Contains(line, "/phpmyadmin/") && strings.Count(line, ":") >= 2 {
                parts := strings.SplitN(line, ":", 3)
                result := fmt.Sprintf("%s|%s|%s", parts[0], parts[1], parts[2])
                writeResult("phpmyadmin.txt", result)
                return
        }

        if strings.Contains(line, "/login/index.php") && strings.Count(line, ":") >= 2 {
                parts := strings.SplitN(line, ":", 3)
                result := fmt.Sprintf("%s|%s|%s", parts[0], parts[1], parts[2])
                writeResult("moodle.txt", result)
                return
        }

        if strings.Contains(line, "/user/login") && strings.Count(line, ":") >= 2 {
                parts := strings.SplitN(line, ":", 3)
                result := fmt.Sprintf("%s|%s|%s", parts[0], parts[1], parts[2])
                writeResult("drupal.txt", result)
                return
        }

        if strings.Contains(line, "/admin") && strings.Contains(line, "/index.php") && strings.Count(line, ":") >= 2 {
                parts := strings.SplitN(line, ":", 3)
                result := fmt.Sprintf("%s|%s|%s", parts[0], parts[1], parts[2])
                writeResult("prestashop.txt", result)
                return
        }
}

func main() {
        if len(os.Args) != 2 {
                fmt.Println("Usage: go run main.go list.txt")
                return
        }

        input := os.Args[1]
        f, err := os.Open(input)
        if err != nil {
                log.Fatalf("[!] Gagal membuka file: %v\n", err)
        }
        defer f.Close()

        reader := bufio.NewReader(f)
        count := 0

        os.MkdirAll("result", 0755)

        for {
                line, err := reader.ReadString('\n')
                if line != "" {
                        extractLine(line)
                        count++
                }
                if err != nil {
                        break
                }
        }

        fmt.Printf("[✓] Extract selesai (%d baris). Cek folder 'result/'\n", count)
}
