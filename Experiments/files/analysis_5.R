setwd("C:/Users/oscarcg/Dropbox/Education/Unimelb PhD/code/Experiments/files/")

library(ggplot2)

res_POIS_3 <- read.csv("experiments_02Apr2017_185401-POIS_3.csv", header = FALSE)
names(res_POIS_3) <- c("alg", "seed", "n_size", "hs_size", "t", "p", "samp", "e_time", "cost", "gr")

p_POIS_3 <- ggplot(res_POIS_3, aes(x=p, y=cost, colour=alg, linetype=alg))
p_POIS_3 <- p_POIS_3 + stat_summary(fun.y = "mean", geom = "smooth")
p_POIS_3 <- p_POIS_3 + scale_x_sqrt(breaks = c(10, 20, 40, 80, 160, 320, 640))
p_POIS_3 <- p_POIS_3 + theme_light()
p_POIS_3 <- p_POIS_3 + labs(x="# POIs", y="Cost")
p_POIS_3

p_POIS_3_et <- ggplot(res_POIS_3, aes(x=p, y=e_time, colour=alg, linetype=alg))
p_POIS_3_et <- p_POIS_3_et + stat_summary(fun.y = "mean", geom = "smooth")
p_POIS_3_et <- p_POIS_3_et + scale_x_sqrt(breaks = c(10, 20, 40, 80, 160, 320, 640))
p_POIS_3_et <- p_POIS_3_et + scale_y_sqrt()
p_POIS_3_et <- p_POIS_3_et + theme_light()
p_POIS_3_et <- p_POIS_3_et + labs(x="# POIs", y="Processing time")
p_POIS_3_et

res_TS_3 <- read.csv("experiments_03Apr2017_172920_TS_3.csv", header = FALSE)
names(res_TS_3) <- c("alg", "seed", "n_size", "hs_size", "t", "p", "samp", "e_time", "cost", "gr")

p_TS_3 <- ggplot(res_TS_3, aes(x=t, y=cost, colour=alg, linetype=alg))
p_TS_3 <- p_TS_3 + stat_summary(fun.y = "mean", geom = "smooth")
p_TS_3 <- p_TS_3 + scale_x_sqrt(breaks = c(2, 4, 8, 16, 32, 64, 128, 256, 512, 1024))
p_TS_3 <- p_TS_3 + theme_light()
p_TS_3 <- p_TS_3 + labs(x="# Users", y="Cost")
p_TS_3

p_TS_3_et <- ggplot(res_TS_3, aes(x=t, y=e_time, colour=alg, linetype=alg))
p_TS_3_et <- p_TS_3_et + stat_summary(fun.y = "mean", geom = "smooth")
p_TS_3_et <- p_TS_3_et + scale_x_sqrt(breaks = c(2, 4, 8, 16, 32, 64, 128, 256, 512, 1024))
p_TS_3_et <- p_TS_3_et + scale_y_sqrt()
p_TS_3_et <- p_TS_3_et + theme_light()
p_TS_3_et <- p_TS_3_et + labs(x="# Users", y="Processing time")
p_TS_3_et

res_N_3 <- read.csv("experiments_03Apr2017_155009_N_3.csv", header = FALSE)
names(res_N_3) <- c("alg", "seed", "n_size", "hs_size", "t", "p", "samp", "e_time", "cost", "gr")

p_N_3 <- ggplot(res_N_3, aes(x=n_size, y=cost, colour=alg, linetype=alg))
p_N_3 <- p_N_3 + stat_summary(fun.y = "mean", geom = "smooth")
p_N_3 <- p_N_3 + scale_x_sqrt(breaks = c(1250, 2500, 5000, 10000, 20000, 40000, 80000))
p_N_3 <- p_N_3 + theme_light()
p_N_3 <- p_N_3 + labs(x="Network size", y="Cost")
p_N_3

p_N_3_et <- ggplot(res_N_3, aes(x=n_size, y=e_time, colour=alg, linetype=alg))
p_N_3_et <- p_N_3_et + stat_summary(fun.y = "mean", geom = "smooth")
p_N_3_et <- p_N_3_et + scale_x_sqrt(breaks = c(1250, 2500, 5000, 10000, 20000, 40000, 80000))
p_N_3_et <- p_N_3_et + scale_y_sqrt()
p_N_3_et <- p_N_3_et + theme_light()
p_N_3_et <- p_N_3_et + labs(x="Network size", y="Processing time")
p_N_3_et