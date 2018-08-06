setwd("C:/Users/oscarcg/Dropbox/Education/Unimelb PhD/code/Experiments/files")

# Dataframes
results <- read.csv("experiments_07JUN2016_1015.csv", header = FALSE)

results_alg_1 <- cbind(results[1:10], 1)
names(results_alg_1) <- c("seed", "nodes", "suit_nodes", "terminals", "sample", "time", "cost", "suit_nodes_st", "deg_more_2", "deg_1", "alg")

results_alg_2 <- cbind(results[1:5], results[11:15], 2)
names(results_alg_2) <- c("seed", "nodes", "suit_nodes", "terminals", "sample", "time", "cost", "suit_nodes_st", "deg_more_2", "deg_1", "alg")

results_ <- rbind(results_alg_1, results_alg_2)

results_$alg <- factor(results_$alg, levels = c(1, 2), labels = c("Spiders", "Ext. Dreyfus"))


contraction <- read.csv("experiments_08JUN2016_contraction.csv", header = FALSE)

contraction_ <- contraction[1:10]
contraction_$alg = 3
names(contraction_) = c("seed", "nodes", "suit_nodes", "terminals", "sample", "time", "cost", "suit_nodes_st", "deg_more_2", "deg_1", "alg")

temp <- subset(results_, alg == 'Spiders' & terminals %in% c(5, 6, 7) & nodes == 8100, select = 1:10)
temp$alg <- 1

contraction_ <- rbind(contraction_, temp)
contraction_$alg <- factor(contraction_$alg, levels = c(1, 3), labels = c("Spiders (Without)", "Spiders (with)"))

# Graphics
library(ggplot2)

ggplot(subset(results_, terminals %in% c(5, 6, 7)), aes(factor(nodes), time)) + geom_boxplot(aes(fill = alg)) + facet_grid(.~terminals) + theme(axis.text.x = element_text(angle = -90))
ggplot(subset(results_, terminals %in% c(8, 9, 10)), aes(factor(nodes), time)) + geom_boxplot(aes(fill = alg)) + facet_grid(.~terminals) + theme(axis.text.x = element_text(angle = -90))

ggplot(subset(results_, terminals %in% c(5, 6, 7)), aes(factor(nodes), cost)) + geom_boxplot(aes(fill = alg)) + facet_grid(.~terminals) + theme(axis.text.x = element_text(angle = -90))
ggplot(subset(results_, terminals %in% c(8, 9, 10)), aes(factor(nodes), cost)) + geom_boxplot(aes(fill = alg)) + facet_grid(.~terminals) + theme(axis.text.x = element_text(angle = -90))

ggplot(subset(results_, terminals %in% c(5, 6, 7)), aes(factor(nodes), suit_nodes_st)) + geom_boxplot(aes(fill = alg)) + facet_grid(.~terminals) + theme(axis.text.x = element_text(angle = -90))
ggplot(subset(results_, terminals %in% c(8, 9, 10)), aes(factor(nodes), suit_nodes_st)) + geom_boxplot(aes(fill = alg)) + facet_grid(.~terminals) + theme(axis.text.x = element_text(angle = -90))

ggplot(subset(results_, terminals %in% c(5, 6, 7)), aes(factor(nodes), deg_more_2)) + geom_boxplot(aes(fill = alg)) + facet_grid(.~terminals) + theme(axis.text.x = element_text(angle = -90))
ggplot(subset(results_, terminals %in% c(8, 9, 10)), aes(factor(nodes), deg_more_2)) + geom_boxplot(aes(fill = alg)) + facet_grid(.~terminals) + theme(axis.text.x = element_text(angle = -90))



ggplot(contraction_, aes(factor(nodes), time)) + geom_boxplot(aes(fill = alg)) + facet_grid(.~terminals) + theme(axis.text.x = element_text(angle = -90))
