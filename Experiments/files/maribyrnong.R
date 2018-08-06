setwd("C:/Users/oscarcg/Dropbox/Education/Unimelb PhD/code/Experiments/files/")

library(ggplot2)

mrb <- read.csv("80 POIs/maribyrnong_3.csv", header = FALSE)
names(mrb) <- c("sa3_code", "dh", "act", "cost", "gr", "avg_dr", "num_cars", "avg_or", "e_time", "id", "Algorithm", "hs_size", "u", "p", "n_size")
mrb$act <- factor(mrb$act, labels = c("Shopping Centre", "Supermarket", "Food store", "Fast food", "Convenience store", "Pub or bar", "Swimming pool"))
mrb[mrb$gr > 10, "gr"] <- NA

p_c <- ggplot(mrb, aes(x=dh, y=cost, colour=act, linetype=Algorithm))
#p_c <- p_c + geom_point(alpha=.3, size=2)
p_c <- p_c + geom_smooth(alpha=.2, size=1)
p_c <- p_c + scale_x_continuous(minor_breaks = c(), breaks = c(7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 23))
p_c <- p_c + my_theme()
p_c <- p_c + labs(x="Departure hour", y="Cost", colour="Activity")
p_c

p_g <- ggplot(mrb, aes(x=dh, y=gr, colour=act, linetype=Algorithm))
p_g <- p_g + geom_point(alpha=.3, size=2)
p_g <- p_g + geom_smooth(alpha=.2, size=1)
p_g <- p_g + scale_x_continuous(minor_breaks = c(), breaks = c(7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 23))
p_g <- p_g + my_theme()
p_g <- p_g + labs(x="Departure hour", y="Gain ratio", colour="Activity")

p_t <- ggplot(mrb, aes(x=dh, y=e_time, colour=act, linetype=Algorithm))
#p_t <- p_t + geom_point(alpha=.3, size=2)
p_t <- p_t + geom_smooth(alpha=.2, size=1)
p_t <- p_t + scale_x_continuous(minor_breaks = c(), breaks = c(7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 23))
p_t <- p_t + my_theme()
p_t <- p_t + labs(x="Departure hour", y="Processing time (s)", colour="Activity")
p_t

p_d <- ggplot(mrb, aes(x=dh, y=avg_dr, colour=act, linetype=Algorithm))
p_d <- p_d + geom_point(alpha=.3, size=2)
p_d <- p_d + geom_smooth(alpha=.2, size=1)
p_d <- p_d + scale_x_continuous(minor_breaks = c(), breaks = c(7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 23))
p_d <- p_d + my_theme()
p_d <- p_d + labs(x="Departure hour", y="Avg. detour ratio", colour="Activity")

p_nc <- ggplot(mrb, aes(x=dh, y=num_cars, colour=act, linetype=Algorithm))
p_nc <- p_nc + geom_point(alpha=.3, size=2)
p_nc <- p_nc + geom_smooth(alpha=.2, size=1)
p_nc <- p_nc + scale_x_continuous(minor_breaks = c(), breaks = c(7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 23))
p_nc <- p_nc + my_theme()
p_nc <- p_nc + labs(x="Departure hour", y="# Cars", colour="Activity")

p_o <- ggplot(mrb, aes(x=dh, y=avg_or, colour=act, linetype=Algorithm))
p_o <- p_o + geom_point(alpha=.3, size=2)
p_o <- p_o + geom_smooth(alpha=.2, size=1)
p_o <- p_o + scale_x_continuous(minor_breaks = c(), breaks = c(7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 23))
p_o <- p_o + my_theme()
p_o <- p_o + labs(x="Departure hour", y="Avg. occupancy ratio", colour="Activity")

multiplot(p_c, p_g, p_t, cols=1)
multiplot(p_d, p_nc, p_o, cols=1)


# To see number of users
with(mrb, tapply(u, list(dh, act), mean))

p <- ggplot(mrb, aes(x=dh, y=u, colour=act))
#p <- p + geom_smooth(alpha=.2, size=1)
p <- p + stat_summary(fun.y = "mean", geom = "smooth")
p <- p + scale_x_continuous(minor_breaks = c(), breaks = c(7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 23))
p <- p + my_theme()
p <- p + labs(x="# Departure hour", y="Avg. number of users", colour="Activity")



# To study frequency of most used meeting points between two methods: meet anywhere vs hot-spots only
mrb_wh_v_woh <- read.csv("maribyrnong/results_24May2017_193731.csv", header = FALSE)
names(mrb_wh_v_woh) <- c("ord", "hotspot_use", "sa3_code", "dh", "act", "cost", "gr", "avg_dr", "num_cars", "avg_or", "e_time", "hs_size", "u", "p", "n_size")
mrb_wh_v_woh$act <- factor(mrb_wh_v_woh$act, labels = c("Shopping Centre", "Supermarket", "Food store", "Fast food", "Convenience store", "Pub or bar", "Swimming pool"))
mrb_wh_v_woh[mrb_wh_v_woh$gr > 10, "gr"] <- NA
mrb_wh_v_woh$sample <- rep(1:170, each=2)

lsv <- read.csv("maribyrnong/lsv_24May2017_193731.csv", header = FALSE)
names(lsv) <- c("ord", "sv", "t", "dist")

merged <- merge(mrb_wh_v_woh, lsv)

library(data.table)
dt_merged <- data.table(merged)
by_sv <- dt_merged[,list(num_people=.N), by=.(act, dh, p, u, hs_size, sample, hotspot_use, sv)]
by_num_people <- by_sv[,list(freq=.N), by=.(act, dh, p, u, hs_size, sample, hotspot_use, num_people)]

library(ggplot2)
p1 <- ggplot(by_sv[act == "Supermarket" & dh == 9 & sample == 2], aes(x = num_people, fill = Algorithm))
p1 <- p1 + geom_histogram(binwidth = 1, position = "dodge")
p1

p2 <- ggplot(by_sv[act == "Shopping Centre"], aes(x = num_people, fill = hotspot_use))
p2 <- p2 + geom_histogram(binwidth = 1, position = "dodge")
p2 <- p2 + my_theme()
p2 <- p2 + labs(x="# People per meeting point", y="# Meeting points")
p2

p3 <- ggplot(by_num_people[act == "Shopping Centre" & freq > 2], aes(x = factor(num_people), y = freq, fill = hotspot_use))
p3 <- p3 + geom_boxplot()
p3 <- p3 + my_theme()
p3 <- p3 + scale_y_log10()
p3 <- p3 + labs(x="# People per meeting point", y="# Meeting points", fill="Hot-spots use")
p3

library(reshape2)
test <- dcast(by_num_people, act + dh + p + u + hs_size + sample + hotspot_use ~ num_people, fun.aggregate = sum, value.var = "freq")
test2 <- dcast(by_num_people, act + hotspot_use ~ num_people, fun.aggregate = sum, value.var = "freq")
test3 <- dcast(by_num_people, act + u + hotspot_use ~ num_people, fun.aggregate = sum, value.var = "freq")


a <- aggregate(mrb_wh_v_woh, by = list(mrb_wh_v_woh$Algorithm, mrb_wh_v_woh$act), FUN = mean)

p <- ggplot(mrb_wh_v_woh, aes(x = Algorithm, y = avg_or, fill = Algorithm))
p <- p + geom_boxplot()
p <- p + theme_light()
p <- p + facet_grid(~act)
p <- p + labs(y = "Avg. occupancy ratio")
p

p3 <- ggplot(mrb_wh_v_woh, aes(x = avg_or, y = avg_dr, colour = Algorithm))
p3 <- p3 + geom_jitter()
p3 <- p3 + theme_light()
# p3 <- p3 + facet_grid(~act)
p3




# To study the behaviour when hot spots' locations vary.
mrb_diff_h_loc <- read.csv("experiments_07JUN2016_1015.csv", header = FALSE)
names(mrb_diff_h_loc) <- c("Algorithm", "sa3_code", "dh", "act", "cost", "gr", "avg_dr", "num_cars", "avg_or", "e_time", "hs_size", "u", "p", "n_size", "sample")
mrb_diff_h_loc$act <- factor(mrb_diff_h_loc$act, labels = c("Shopping Centre", "Supermarket", "Food store", "Fast food", "Convenience store", "Pub or bar", "Restaurant or cafe", "Swimming pool"))
mrb_diff_h_loc[mrb_diff_h_loc$gr > 10, "gr"] <- NA

p <- ggplot(subset(mrb_diff_h_loc, subset = act != "Restaurant or cafe"), aes(x = Algorithm, y = avg_or, fill = Algorithm))
p <- p + geom_boxplot()
p <- p + theme_light()
p <- p + facet_grid(~act)
p <- p + labs(y = "Avg. occupancy ratio")
p


# To study change in gap when awareness changes.
mrb_awareness <- read.csv("results_26Jun2017_021821.csv", header = FALSE)
names(mrb_awareness) <- c("ord", "Placement", "hotspot_use", "sa3_code", "dh", "act", "cost", "gr", "avg_dr", "num_cars", "avg_or", "avg_oc", "e_time", "hs_size", "u", "p", "n_size", "sample")
mrb_awareness$act <- factor(mrb_awareness$act, labels = c("Shopping Centre", "Supermarket", "Food store", "Fast food", "Convenience store", "Pub or bar", "Restaurant or cafe", "Swimming pool"))
mrb_awareness$sample <- factor(mrb_awareness$sample)
mrb_awareness[mrb_awareness$gr > 10, "gr"] <- NA

temp <- data.table(mrb_awareness)

p <- ggplot(data = temp[act == "Shopping Centre"], mapping = aes(x = hotspot_use, y = avg_oc, colour = Placement))
p <- p + geom_smooth(alpha=.2, size=1)
p <- p + scale_x_continuous(breaks = c(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0), labels=c("10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"))
p <- p + my_theme()
p <- p + labs(x="Hot-spot use", y="Avg. occupancy ratio")
p


p <- ggplot(data = temp[act == "Food store"], mapping = aes(x = hotspot_use, y = avg_oc, colour = Placement))
p <- p + geom_smooth(alpha=.2, size=1)
p <- p + scale_x_continuous(breaks = c(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0), labels=c("10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"))
p <- p + my_theme()
p <- p + labs(x="Hot-spot use", y="Avg. occupancy ratio")
p


ggplot(data = temp[act == "Supermarket" & dh == 9 & sample == 0], mapping = aes(x = awareness, y = avg_oc, colour = Algorithm)) + geom_line()

ggplot(data = temp[Algorithm == "original"], mapping = aes(x = factor(dh), y = avg_oc)) + geom_boxplot() + facet_grid(.~act, scales = "free")
ggplot(data = temp[Algorithm == "random"], mapping = aes(x = factor(dh), y = avg_oc)) + geom_boxplot() + facet_grid(.~act, scales = "free")
ggplot(data = temp[Algorithm == "clustered"], mapping = aes(x = factor(dh), y = avg_oc)) + geom_boxplot() + facet_grid(.~act, scales = "free")

ggplot(data = temp[Algorithm == "original" & awareness == 0], mapping = aes(x = factor(dh), y = avg_oc)) + geom_boxplot() + facet_grid(.~act, scales = "free")
ggplot(data = temp[Algorithm == "original" & awareness == 1], mapping = aes(x = factor(dh), y = avg_oc)) + geom_boxplot() + facet_grid(.~act, scales = "free")
