setwd("C:/Users/oscarcg/Dropbox/Education/Unimelb PhD/code/Experiments/files/")

library(ggplot2)

res <- read.csv("experiments_03Mar2017_185515.csv", header = FALSE)
names(res) <- c("alg", "seed", "n_size", "hs_size", "t", "p", "samp", "e_time", "cost", "sp")
res$t <- res$t - res$p
#res$hs_bins <- cut(res$hs_size, seq(min(res$hs_size), max(res$hs_size), 10), include.lowest = TRUE)

plot_e_time <- function(nsize) {
  data <- subset(x = res, subset = n_size==nsize)
  ggplot(data, aes(x=hs_size, y=e_time, colour=alg, z=t)) + 
    geom_point() + 
    facet_wrap(~p) +
    scale_y_log10() +
    stat_summary(fun.y = "median", geom = "smooth") +
    stat_summary_2d(show.legend = FALSE) +
    theme_light() +
    labs(x="# hot-spots", y="Processing time", colour="Algorithm")
}

plot_cost <- function(nsize) {
  data <- subset(x = res, subset = n_size==nsize)
  ggplot(data, aes(x=hs_size, y=cost, colour=alg, z=t)) + 
    geom_point() + 
    facet_wrap(~p) +
    stat_summary(fun.y = "median", geom = "smooth") +
    stat_summary_2d(show.legend = FALSE) +
    theme_light() +
    labs(x="# hot-spots", y="Travel cost", colour="Algorithm")
}

plot_e_time(2500)
plot_cost(2500)

plot_e_time(3600)
plot_cost(3600)

plot_e_time(4900)
plot_cost(4900)

plot_e_time(6400)
plot_cost(6400)

plot_e_time(8100)
plot_cost(8100)

plot_e_time(10000)
plot_cost(10000)