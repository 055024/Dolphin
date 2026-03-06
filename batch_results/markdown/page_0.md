PATTERN FOR PYTHON

pattern.graph Graph data structure using Node , Edge and Graph classes, useful (for example) for modeling semantic networks. The module has algorithms for shortest path finding, subgraph partitioning, eigenvector centrality and betweenness centrality (Brandes, 2001) . Centrality algorithms were ported from NETWORKX . The module has a force-based layout algorithm that positions nodes in 2D space. Visualizations can be exported to HTML and manipulated in a browser (using our canvas.js helper module for the HTML5 Canvas2D element).

pattern.metrics Descriptive statistics functions. Evaluation metrics including a code profiler, functions for accuracy, precision and recall, confusion matrix, inter-rater agreement (Fleiss' kappa), string similarity (Levenshtein, Dice) and readability (Flesch).

pattern.db Wrappers for CSV files and SQLITE and MYSQL databases.

## 3. Example Script

As an example, we chain together four PATTERN modules to train a $k$ -NN classifier on adjectives mined from Twitter. First, we mine 1,500 tweets with the hashtag # win or # fail (our classes), for example: “ $20 tip off a sweet little old lady today # win ” . We parse the part-of-speech tags for each tweet, keeping adjectives. We group the adjective vectors in a corpus and use it to train the classifier. It predicts “ sweet ” as WIN and “ stupid ” as FAIL . The results may vary depending on what is currently buzzing on Twitter.

The source code is shown in Figure 2 . Its size is representative for many real-world scenarios, although a real-world classifier may need more training data and more rigorous feature selection.

```bash
from pattern.web    import Twitter
from pattern.en    import Sentence, parse
from pattern.search import search
from pattern.vector import Document, Corpus, KNN
corpus = Corpus()
for i in range(1,15):
    for tweet in Twitter().search('#win OR #fail', start=i, count=100):
        p = '#win' in tweet.description.lower() and 'WIN' or 'FAIL'
        s = tweet.description.lower()
        s = Sentence(parse(s))
        s = search('JJ', s)  # JJ = adjective
        s = [match[0].string for match in s]
        s = ' '.join(s)
        if len(s) > 0:
            corpus.append(Document(s, type=p))
classifier = KNN()
for document in corpus:
    classifier.train(document)
print classifier.classify('sweet')  # yields 'WIN'
print classifier.classify('stupid')  # yields 'FAIL'd
```

Figure 2: Example source code for a $k$-NN classifier trained on Twitter messages.

2065

