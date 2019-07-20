# Title     : TODO
# Objective : TODO
# Created by: oscar
# Created on: 2019-07-19

library(data.table)
library(ggplot2)

setwd("../Pickup-Delivery/test/files/")

set_1 <- fread("csdp_ap_19Jul2019_163223.csv", header = TRUE)
set_2 <- fread("csdp_ap_19Jul2019_175046.csv", header = TRUE)
set_3 <- fread("csdp_ap_20Jul2019_112800.csv", header = TRUE)

expr <- rbind(set_1, set_2, set_3)


ratio <- function(sd) {
  opt <- sd[!endsWith(Approach, "-DT"), -1, with = FALSE]
  appr <- sd[endsWith(Approach, "-DT"), -1, with = FALSE]
  if(nrow(opt) == 1 & nrow(appr) == 1){
    appr[1] / opt[1]
  }
}

sd_cols <- c("Approach", "Cost", "Elapsed.time", "Ad.hoc.cost", "Dedicated.cost", "Num.ded")

vor <- expr[Approach == "SP-Voronoi" | Approach == "SP-Voronoi-DT", cbind("Voronoi", ratio(.SD)), by = list(Seed, Net.size), .SDcols = sd_cols]
exp_01 <- expr[(Approach == "SP-fraction" | Approach == "SP-fraction-DT") & Param == 0.1, cbind("Fr: 0.1", ratio(.SD)), by = list(Seed, Net.size), .SDcols = sd_cols]
exp_02 <- expr[(Approach == "SP-fraction" | Approach == "SP-fraction-DT") & Param == 0.2, cbind("Fr: 0.2", ratio(.SD)), by = list(Seed, Net.size), .SDcols = sd_cols]
exp_03 <- expr[(Approach == "SP-fraction" | Approach == "SP-fraction-DT") & Param == 0.3, cbind("Fr: 0.3", ratio(.SD)), by = list(Seed, Net.size), .SDcols = sd_cols]
exp_04 <- expr[(Approach == "SP-fraction" | Approach == "SP-fraction-DT") & Param == 0.4, cbind("Fr: 0.4", ratio(.SD)), by = list(Seed, Net.size), .SDcols = sd_cols]
exp_05 <- expr[(Approach == "SP-fraction" | Approach == "SP-fraction-DT") & Param == 0.5, cbind("Fr: 0.5", ratio(.SD)), by = list(Seed, Net.size), .SDcols = sd_cols]
thr_15 <- expr[(Approach == "SP-threshold" | Approach == "SP-threshold-DT") & Param == 1.5, cbind("Thr: 1.5", ratio(.SD)), by = list(Seed, Net.size), .SDcols = sd_cols]
thr_16 <- expr[(Approach == "SP-threshold" | Approach == "SP-threshold-DT") & Param == 1.6, cbind("Thr: 1.6", ratio(.SD)), by = list(Seed, Net.size), .SDcols = sd_cols]
thr_17 <- expr[(Approach == "SP-threshold" | Approach == "SP-threshold-DT") & Param == 1.7, cbind("Thr: 1.7", ratio(.SD)), by = list(Seed, Net.size), .SDcols = sd_cols]
thr_18 <- expr[(Approach == "SP-threshold" | Approach == "SP-threshold-DT") & Param == 1.8, cbind("Thr: 1.8", ratio(.SD)), by = list(Seed, Net.size), .SDcols = sd_cols]
thr_19 <- expr[(Approach == "SP-threshold" | Approach == "SP-threshold-DT") & Param == 1.9, cbind("Thr: 1.9", ratio(.SD)), by = list(Seed, Net.size), .SDcols = sd_cols]
thr_20 <- expr[(Approach == "SP-threshold" | Approach == "SP-threshold-DT") & Param == 2.0, cbind("Thr: 2.0", ratio(.SD)), by = list(Seed, Net.size), .SDcols = sd_cols]

bb_dt <- rbind(vor, exp_01, exp_02, exp_03, exp_04, exp_05, thr_15, thr_16, thr_17, thr_18, thr_19, thr_20)

names(bb_dt)[names(bb_dt) == "V1"] <- "Approach"

my_theme <- function(base_size = 11, base_family = "") {
  # Starts with theme_grey and then modify some parts
  theme_grey(base_size = base_size, base_family = base_family) %+replace%
    theme(
      # white panel with light grey border
      panel.background = element_rect(fill = "white", colour = NA),
      panel.border     = element_rect(fill = NA, colour = "grey70", size = 0.5),
      # light grey, thinner gridlines
      # => make them slightly darker to keep acceptable contrast
      #panel.grid.major = element_line(colour = "grey87", size = 0.25),
      #panel.grid.minor = element_line(colour = "grey87", size = 0.125),

      # match axes ticks thickness to gridlines and colour to panel border
      axis.ticks       = element_line(colour = "grey70", size = 0.25),

      # match legend key to panel.background
      #legend.key           = element_rect(fill = "white", colour = NA),

      legend.position      = "none",

      legend.background    = element_rect(fill = "white", size = 4, colour = "white"),
      legend.justification = c(1, 0),
      #legend.position      = c(1, 0),
      legend.title         = element_text(size = 10, lineheight = 0.9, colour = "black", hjust = 1, face="bold"),
      legend.text          = element_text(size = 10, lineheight = 0.9, colour = "black", hjust = 1),

      #legend.text           = element_text(size = 8, lineheight = 0.9, hjust = 1),
      #legend.title          = element_text(size = 9),

      # dark strips with light text (inverse contrast compared to theme_grey)
      strip.background = element_rect(fill = "grey70", colour = NA),
      strip.text       = element_text(colour = "white", size = rel(0.8)),

      #axis.title.x = axis_x_title,
      #axis.title.y = axis_y_title,
      axis.title.x = element_text(size = 10, vjust = 0.5, face="bold"),
      axis.title.y = element_text(size = 10, angle = 90, vjust = 0.5, face="bold"),
      #axis.text    = element_text(size = 8, lineheight = 0.9, colour = "grey50", hjust = 1),
      axis.text    = element_text(size = 10, lineheight = 0.9, colour = "black", hjust = 1),

      complete = TRUE
    )

}


p1 <- ggplot(bb_dt, aes(x = Approach, y = Cost, fill = Approach))
p1 <- p1 + geom_boxplot()
p1 <- p1 + scale_x_discrete()
p1 <- p1 + my_theme()
p1 <- p1 + labs(y = "Ratio costs")
p1

p2 <- ggplot(bb_dt, aes(x = Approach, y = Elapsed.time, fill = Approach))
p2 <- p2 + geom_boxplot()
p2 <- p2 + scale_x_discrete()
p2 <- p2 + my_theme()
p2 <- p2 + labs(y = "Ratio processing times")
p2

p3 <- ggplot(bb_dt, aes(x = Approach, y = Dedicated.cost, fill = Approach))
p3 <- p3 + geom_boxplot()
p3 <- p3 + scale_x_discrete()
p3 <- p3 + my_theme()
p3 <- p3 + labs(y = "Ratio dedicated costs")
p3