setwd("C:/Users/oscarcg/Dropbox/Education/Unimelb PhD/code/Experiments/files")
#setwd("C:/Users/Oscar/Dropbox/Education/Unimelb PhD/code/Experiments/files")


# Dataframes

# 6 terminals
# results <- read.csv("experiments_18Jun2016_080508.csv", header = FALSE)

# 20 terminals
# results <- read.csv("experiments_18Jun2016_105535.csv", header = FALSE)
# results <- read.csv("experiments_18Jun2016_132135.csv", header = FALSE)

# 10 terminals w/ Dreyfus
# results <- read.csv("experiments_18Jun2016_160419.csv", header = FALSE)

# 6 terminals w/ Dreyfus (complete)
results <- read.csv("experiments_19Jun2016_011712.csv", header = FALSE)
names(results) <- c("alg", "seed", "nodes", "suit_nodes", "terminals", "dijkstra", "sample", "time", "cost", "suit_nodes_st", "deg_more_2", "deg_1")

# 6 terminals w/ further extended Dreyfus (complete)
results <- read.csv("experiments_23Jun2016_145135.csv", header = FALSE)
names(results) <- c("alg", "seed", "nodes", "suit_nodes", "terminals", "dijkstra", "sample", "time", "cost", "suit_nodes_st", "deg_more_2", "deg_1")

# 6 terminals w/ further extended Dreyfus (complete)
results <- read.csv("experiments_23Jun2016_154418.csv", header = FALSE)
names(results) <- c("alg", "seed", "nodes", "suit_nodes", "terminals", "dijkstra", "sample", "time", "cost", "suit_nodes_st", "deg_more_2", "deg_1")

# 6 - 10 terminals w/ further extended Dreyfus (complete)
results <- read.csv("experiments_23Jun2016_235443.csv", header = FALSE)
names(results) <- c("alg", "seed", "nodes", "suit_nodes", "terminals", "dijkstra", "sample", "time", "cost", "suit_nodes_st", "deg_more_2", "deg_1")


# 6 terminals w/ 5% suitable nodes and extensions. Moreover, including checking dijkstra paths go through suitable nodes and then give more weight (1).
results_1 <- read.csv("experiments_20Jun2016_130839.csv", header = FALSE)
names(results_1) <- c("alg", "seed", "nodes", "suit_nodes", "terminals", "dijkstra", "sample", "time", "cost", "suit_nodes_st", "deg_more_2", "deg_1")
ggplot(results_1, aes(factor(nodes), cost)) + geom_boxplot(aes(fill = alg))
ggplot(results_1, aes(factor(nodes), suit_nodes_st)) + geom_boxplot(aes(fill = alg))
ggplot(results_1, aes(factor(nodes), deg_more_2)) + geom_boxplot(aes(fill = alg))

# 6 terminals w/ (1) and attraction from POI (2).
results_2 <- read.csv("experiments_20Jun2016_143243.csv", header = FALSE)
names(results_2) <- c("alg", "seed", "nodes", "suit_nodes", "terminals", "dijkstra", "sample", "time", "cost", "suit_nodes_st", "deg_more_2", "deg_1")
ggplot(results_2, aes(factor(nodes), cost)) + geom_boxplot(aes(fill = alg))
ggplot(results_2, aes(factor(nodes), suit_nodes_st)) + geom_boxplot(aes(fill = alg))
ggplot(results_2, aes(factor(nodes), deg_more_2)) + geom_boxplot(aes(fill = alg))

# 6 terminals w/ (1) but w/ more value to hits(3).
results_3 <- read.csv("experiments_20Jun2016_145433.csv", header = FALSE)
names(results_3) <- c("alg", "seed", "nodes", "suit_nodes", "terminals", "dijkstra", "sample", "time", "cost", "suit_nodes_st", "deg_more_2", "deg_1")
ggplot(results_3, aes(factor(nodes), cost)) + geom_boxplot(aes(fill = alg))
ggplot(results_3, aes(factor(nodes), suit_nodes_st)) + geom_boxplot(aes(fill = alg))
ggplot(results_3, aes(factor(nodes), deg_more_2)) + geom_boxplot(aes(fill = alg))

# 10 terminals (3)
results_4 <- read.csv("experiments_20Jun2016_151656.csv", header = FALSE)
names(results_4) <- c("alg", "seed", "nodes", "suit_nodes", "terminals", "dijkstra", "sample", "time", "cost", "suit_nodes_st", "deg_more_2", "deg_1")
ggplot(results_4, aes(factor(nodes), time)) + geom_boxplot(aes(fill = alg))
ggplot(results_4, aes(factor(nodes), cost)) + geom_boxplot(aes(fill = alg))
ggplot(results_4, aes(factor(nodes), suit_nodes_st)) + geom_boxplot(aes(fill = alg))
ggplot(results_4, aes(factor(nodes), deg_more_2)) + geom_boxplot(aes(fill = alg))

# Graphics
library(ggplot2)

r <- subset(results, nodes < 900)
p0 <- ggplot(r, aes(factor(nodes), time)) + geom_boxplot(aes(fill = alg), outlier.colour = NA)
sts <- boxplot.stats(r$time)$stats
p1 <- p0 + coord_cartesian(ylim = c(sts[2] / 2, max(sts) * 1.2))
p1

r <- subset(results, nodes >= 900 & nodes < 3600)
p0 <- ggplot(r, aes(factor(nodes), time)) + geom_boxplot(aes(fill = alg), outlier.colour = NA)
sts <- boxplot.stats(r$time)$stats
p1 <- p0 + coord_cartesian(ylim = c(sts[2] / 2, max(sts) * 1.8))
p1

r <- subset(results, nodes >= 3600 & nodes < 8100)
p0 <- ggplot(r, aes(factor(nodes), time)) + geom_boxplot(aes(fill = alg), outlier.colour = NA)
sts <- boxplot.stats(r$time)$stats
p1 <- p0 + coord_cartesian(ylim = c(sts[2] / 2, max(sts) * 1.8))
p1

r <- subset(results, nodes >= 8100)
p0 <- ggplot(r, aes(factor(nodes), time)) + geom_boxplot(aes(fill = alg), outlier.colour = NA)
sts <- boxplot.stats(r$time)$stats
p1 <- p0 + coord_cartesian(ylim = c(sts[2] / 2, max(sts) * 1.05))
p1


ggplot(results, aes(factor(nodes), time)) + geom_boxplot(aes(fill = alg)) + facet_grid(.~terminals)

ggplot(results, aes(factor(nodes), cost)) + geom_boxplot(aes(fill = alg)) + facet_grid(.~terminals)
# ggplot(subset(results, nodes <= 4900), aes(factor(nodes), cost)) + geom_boxplot(aes(fill = alg))

ggplot(results, aes(factor(nodes), suit_nodes_st)) + geom_boxplot(aes(fill = alg)) + facet_grid(.~terminals)

ggplot(results, aes(factor(nodes), deg_more_2)) + geom_boxplot(aes(fill = alg)) + facet_grid(.~terminals)


# Analysis of some results
