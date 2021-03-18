# umdparser
Automatically exported from code.google.com/p/umdparser

Example:
```
import umd

filename = 'output.umd'

umdfile = umd.UMDFile()
umdfile.title = 'book name'
umdfile.author = 'author'
for title, content in iter_chapter():
  chapter = umd.Chapter(title, content)
  umdfile.chapters.append(chapter)

with open(filename, 'wb') as f:
  umdfile.write(f)

```
