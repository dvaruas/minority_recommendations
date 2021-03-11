# Recommending minorities in Online Social Network

Master thesis work at RWTH Aachen University.

**Abstract :**

Recommender systems form an integral part of Online Social network communities and play a crucial role in shaping the evolution of network structures. Thus, it is important to understand how much of the bias is seen in the user recommendations provided by these agents and their effect on the network over a period of time. We consider synthetic networks with different homophilies and minority group sizes and perform experiments with several recommender agents to systematically study this kind of bias. We also grow networks under the influence of several recommender systems (much like in a real-world setting) and analyze the evolved network structures. Through our study we find that recommendation methods like Adamic-Adar or Twitter-Rank leads to the formation of unbiased networks and has a balanced visibility for both groups in a network relative to their respective group sizes. Finally we also use recommendation methods on some empirical Facebook networks to analyze the bias in visibility for different node groups in the recommendations provided by our recommendation methods.

---

## Project structure

### data
* **crawled :** data from the [Facebook100](http://masonporter.blogspot.com/2011/02/facebook100-data-set.html) dataset.
* **synthetic :** synthetic networks created using [Karimi et. al.](https://www.nature.com/articles/s41598-018-29405-7) method.

### src
* **code :** all source code for experiments
  * **common :** contains recommenders code and other managing and network building codes.
  * **crawled_data :** code for crawling data for Facebook100.
  * **growth_network :** code for experiments with the Growing OSN variant.
  * **plot_computations :** computing logic for various plots drawn.
  * **plots :** plot scripts using the plot_computations code.
  * **static_network :** code for experiments with the Static OSN variant.
* **proposal :** LateX files for thesis proposal document
* **thesis :** LateX files for final thesis document
