# PageRank

A simple Python Search Spider, Page Ranker, and Visualizer

### Prerequisites

Install the Beautiful Soup 4 package:

```
pip install beautifulsoup4
```

### Usage

The program **spider.py** crawls a web site and pulls a series of pages into the database, recording the links between pages in a database file **spider.sqlite**.
The file spider.sqlite can be removed at any time to restart the process.

```
del spider.sqlite
python spider.py

Output:
Enter the web url to crawl: http://harrypotter.wikia.com/wiki/Main_Page
['http://harrypotter.wikia.com/wiki/Main_Page']
How many pages to crawl? 3
1 http://harrypotter.wikia.com/wiki/Main_Page (192998) 9
3 http://harrypotter.wikia.com/wiki/Main_Page?action=history (170450) 171
77 http://harrypotter.wikia.com/wiki/Main_Page?oldid=1030936 (173210) 16
How many pages to crawl?
```

In this run, we told the program to crawl a website and retrieve three pages.
If you restart the program again and tell it to crawl more pages, it will not re-crawl any pages already in the database.
Upon restart it goes to a random non-crawled page and starts there.
So each successive run of spider.py is additive.

```
python spider.py

Output:
How many pages to crawl? 5
86 http://harrypotter.wikia.com/wiki/Main_Page?oldid=1023626 (179559) 15
44 http://harrypotter.wikia.com/wiki/Main_Page?oldid=1050952 (188275) 15
19 http://harrypotter.wikia.com/wiki/Main_Page?diff=1055812&oldid=1054675 (186797) 16
26 http://harrypotter.wikia.com/wiki/Main_Page?oldid=1054226 (190430) 15
84 http://harrypotter.wikia.com/wiki/Main_Page?diff=1073386&oldid=1023626 (203212) 15
How many pages to crawl?
```

You can have multiple starting points in the same database, within the program. These are called "webs".
The spider chooses randomly amongst all non-visited links across all the webs.

If you want to dump the contents of the spider.sqlite file, you can run **dump.py** as follows:

```
python dump.py

Output:
(28, None, 1.0, 1, 'http://harrypotter.wikia.com/wiki/Main_Page')
(10, None, 1.0, 3, 'http://harrypotter.wikia.com/wiki/Main_Page?action=history')
(7, None, 1.0, 86, 'http://harrypotter.wikia.com/wiki/Main_Page?oldid=1023626')
(6, None, 1.0, 26, 'http://harrypotter.wikia.com/wiki/Main_Page?oldid=1054226')
(6, None, 1.0, 44, 'http://harrypotter.wikia.com/wiki/Main_Page?oldid=1050952')
(5, None, 1.0, 19, 'http://harrypotter.wikia.com/wiki/Main_Page?diff=1055812&oldid=1054675')
(5, None, 1.0, 77, 'http://harrypotter.wikia.com/wiki/Main_Page?oldid=1030936')
(4, None, 1.0, 84, 'http://harrypotter.wikia.com/wiki/Main_Page?diff=1073386&oldid=1023626')
8 rows.
```

This shows the number of incoming links, the old page rank, the new page rank, the id of the page, and the url of the page.
The dump.py program only shows pages that have at least one incoming link to them.

Once you have a few pages in the database, you can run Page Rank on the pages using the **rank.py** program.
You simply tell it how many Page Rank iterations to run.

```
python rank.py

Output:
How many iterations? 5
1 1.2023809523809526
2 0.5357142857142861
3 0.2643140589569164
4 0.22874149659863907
5 0.18590729942770728
[(1, 1.6907056473383002), (3, 3.0872071050642473), (77, 0.5156300615484289), (86, 0.6439369398553073), (44, 0.5156300615484289)]
```

You can dump the database again to see that page rank has been updated:

```
python dump.py

Output:
(28, 1.0, 1.6907056473383002, 1, 'http://harrypotter.wikia.com/wiki/Main_Page')
(10, 1.0, 3.0872071050642473, 3, 'http://harrypotter.wikia.com/wiki/Main_Page?action=history')
(7, 1.0, 0.6439369398553073, 86, 'http://harrypotter.wikia.com/wiki/Main_Page?oldid=1023626')
(6, 1.0, 0.5156300615484289, 26, 'http://harrypotter.wikia.com/wiki/Main_Page?oldid=1054226')
(6, 1.0, 0.5156300615484289, 44, 'http://harrypotter.wikia.com/wiki/Main_Page?oldid=1050952')
(5, 1.0, 0.5156300615484289, 19, 'http://harrypotter.wikia.com/wiki/Main_Page?diff=1055812&oldid=1054675')
(5, 1.0, 0.5156300615484289, 77, 'http://harrypotter.wikia.com/wiki/Main_Page?oldid=1030936')
(4, 1.0, 0.5156300615484289, 84, 'http://harrypotter.wikia.com/wiki/Main_Page?diff=1073386&oldid=1023626')
8 rows.
```

You can run rank.py as many times as you like and it will simply refine the page rank the more times you run it.
You can even run rank.py a few times and then go spider a few more pages with spider.py and then run rank.py to converge the page ranks.

If you want to restart the Page Rank calculations without re-spidering the web pages, you can use **rank_reset.py**

```
python rank_reset.py

Output:
All pages are now set to a rank of 1.0

python rank.py

Output:
How many iterations? 50
1 1.2023809523809526
2 0.5357142857142861
3 0.2643140589569164
4 0.22874149659863907
5 0.18590729942770728
...
45 1.3429741277382057e-09
46 6.168515767623894e-10
47 4.868911315791813e-10
48 3.9942717189322963e-10
49 2.4144617555288406e-10
50 1.0023677721182622e-10
[(1, 1.8461538462837153), (3, 3.2307692306330926), (77, 0.4615384615365238), (86, 0.61538461540059), (44, 0.4615384615365238)]
```
For each iteration of the page rank algorithm, it prints the average change per page of the page rank.
The network initially is quite unbalanced and so the individual page ranks are changing wildly.
But in a few short iterations, the page rank converges.
You should run rank.py long enough so that the page ranks converge.

If you want to visualize the current top pages in terms of page rank, run **json.py** to write the pages out in JSON format to be viewed in a web browser.

```
python json.py

Output:
Creating JSON output on spider.js.
How many nodes? 25
Open visualize.html in a browser to view the visualization.
```

You can view this data by opening the file **visualize.html** in your web browser.  
This shows an automatic layout of the nodes and links.
You can click and drag any node and you can also double click on a node to find the URL that is represented by the node.

This visualization is provided using the force layout from:
http://mbostock.github.com/d3/

If you re-run the other utilities and then re-run json.py, you merely have to press refresh in the browser to get the new data from **spider.js**.

## Authors

* **Prathamesh Kumkar** - [iPrathamKumkar](https://github.com/iPrathamKumkar)

## Acknowledgments

* Special thanks to Mr. Charles Severance Mr. Michael Bostock!
