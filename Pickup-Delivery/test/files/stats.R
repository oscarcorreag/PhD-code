library(data.table)
library(ggplot2)

setwd("C:/Users/oscarcg/Documents/phd/code/Pickup-Delivery/test/files/")

exp <- fread("csdp_ap_08Aug2019_204716.csv")
exp <- exp[startsWith(exp$Approach, "MILP") | endsWith(exp$Approach, "DT")]
exp$Total.cust <- exp$Num.retailers * exp$Cust.ret
exp$Total.drv <- exp$Num.retailers * exp$Drv.ret
exp$Ad.hoc.cost.prop <- exp$Ad.hoc.cost / exp$Cost
exp$Ded.cost.prop <- 1 - exp$Ad.hoc.cost.prop

ratio <- function(sd) {
  opt <- sd[Approach == "MILP", -1, with = FALSE]
  appr <- sd[Approach != "MILP", -1, with = FALSE]
  if(nrow(opt) == 1 & nrow(appr) == 1){
    appr[1] / opt[1]
  }
}

ratio_th <- function(sd) {
  opt <- sd[Approach == "MILP-threshold", -1, with = FALSE]
  appr <- sd[Approach != "MILP-threshold", -1, with = FALSE]
  if(nrow(opt) == 1 & nrow(appr) == 1){
    appr[1] / opt[1]
  }
}

sd_cols <- c("Approach", "Cost", "Elapsed.time")

MILP <- exp[Seed %in% exp[Approach == "MILP", Seed]]

MILP_Vor <- MILP[Approach == "MILP" | Approach == "SP-Voronoi-DT", cbind("Voronoi", ratio(.SD)), by = Seed, .SDcols = sd_cols]
MILP_Exp_01 <- MILP[Approach == "MILP" | (Approach == "SP-fraction-DT" & Param == 0.1), cbind("Fr: 0.1", ratio(.SD)), by = Seed, .SDcols = sd_cols]
MILP_Exp_02 <- MILP[Approach == "MILP" | (Approach == "SP-fraction-DT" & Param == 0.2), cbind("Fr: 0.2", ratio(.SD)), by = Seed, .SDcols = sd_cols]
MILP_Exp_03 <- MILP[Approach == "MILP" | (Approach == "SP-fraction-DT" & Param == 0.3), cbind("Fr: 0.3", ratio(.SD)), by = Seed, .SDcols = sd_cols]
MILP_Exp_04 <- MILP[Approach == "MILP" | (Approach == "SP-fraction-DT" & Param == 0.4), cbind("Fr: 0.4", ratio(.SD)), by = Seed, .SDcols = sd_cols]
MILP_Exp_05 <- MILP[Approach == "MILP" | (Approach == "SP-fraction-DT" & Param == 0.5), cbind("Fr: 0.5", ratio(.SD)), by = Seed, .SDcols = sd_cols]

MILP_th <- exp[Seed %in% exp[Approach == "MILP-threshold", Seed]]

MILP_th_Th_15 <- MILP_th[(Approach == "MILP-threshold" | Approach == "SP-threshold-DT") & Param == 1.5, cbind("Thr: 1.5", ratio_th(.SD)), by = Seed, .SDcols = sd_cols]
MILP_th_Th_16 <- MILP_th[(Approach == "MILP-threshold" | Approach == "SP-threshold-DT") & Param == 1.6, cbind("Thr: 1.6", ratio_th(.SD)), by = Seed, .SDcols = sd_cols]
MILP_th_Th_17 <- MILP_th[(Approach == "MILP-threshold" | Approach == "SP-threshold-DT") & Param == 1.7, cbind("Thr: 1.7", ratio_th(.SD)), by = Seed, .SDcols = sd_cols]
MILP_th_Th_18 <- MILP_th[(Approach == "MILP-threshold" | Approach == "SP-threshold-DT") & Param == 1.8, cbind("Thr: 1.8", ratio_th(.SD)), by = Seed, .SDcols = sd_cols]
MILP_th_Th_19 <- MILP_th[(Approach == "MILP-threshold" | Approach == "SP-threshold-DT") & Param == 1.9, cbind("Thr: 1.9", ratio_th(.SD)), by = Seed, .SDcols = sd_cols]
MILP_th_Th_20 <- MILP_th[(Approach == "MILP-threshold" | Approach == "SP-threshold-DT") & Param == 2.0, cbind("Thr: 2.0", ratio_th(.SD)), by = Seed, .SDcols = sd_cols]

v_opt <- rbind(MILP_Vor, MILP_Exp_01, MILP_Exp_02, MILP_Exp_03, MILP_Exp_04, MILP_Exp_05)
v_thr <- rbind(MILP_th_Th_15, MILP_th_Th_16, MILP_th_Th_17, MILP_th_Th_18, MILP_th_Th_19, MILP_th_Th_20)

names(v_opt)[names(v_opt) == "V1"] <- "Approach"
names(v_thr)[names(v_thr) == "V1"] <- "Approach"

v_opt$Approach <- as.factor(v_opt$Approach)
v_thr$Approach <- as.factor(v_thr$Approach)


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

p1 <- ggplot(v_opt, aes(x = Approach, y = Cost, fill = Approach))
p1 <- p1 + geom_boxplot()
p1 <- p1 + scale_x_discrete()
p1 <- p1 + my_theme()
p1 <- p1 + labs(y = "Ratio costs")
p1

p2 <- ggplot(v_opt, aes(x = Approach, y = Elapsed.time, fill = Approach))
p2 <- p2 + geom_boxplot()
p2 <- p2 + scale_x_discrete()
p2 <- p2 + scale_y_log10(breaks = c(0, .0001, .001, .01, .1))
p2 <- p2 + my_theme()
p2 <- p2 + labs(y = "Ratio processing times")
p2

v_thr[Cost - 1 < .0001]

p3 <- ggplot(v_thr, aes(x = Approach, y = Cost, fill = Approach))
p3 <- p3 + geom_boxplot()
p3 <- p3 + scale_fill_brewer(palette="Pastel1")
p3 <- p3 + scale_x_discrete()
p3 <- p3 + my_theme()
p3 <- p3 + labs(y = "Ratio costs")
p3

p4 <- ggplot(v_thr, aes(x = Approach, y = Elapsed.time, fill = Approach))
p4 <- p4 + geom_boxplot()
p4 <- p4 + scale_fill_brewer(palette="Pastel1")
p4 <- p4 + scale_x_discrete()
p4 <- p4 + scale_y_log10(breaks = c(0, .0001, .001, .01, .1, 1.))
#p4 <- p4 + scale_y_log10()
p4 <- p4 + my_theme()
p4 <- p4 + labs(y = "Ratio processing times")
p4

p5 <- ggplot(MILP_th[Approach %in% c("MILP", "MILP-threshold", "SP-threshold-DT")], aes(x = Approach, y = Avg.detour, fill = Approach))
p5 <- p5 + geom_boxplot()
p5 <- p5 + scale_fill_brewer(palette="Set1")
p5 <- p5 + scale_x_discrete()
p5 <- p5 + scale_y_log10(breaks = c(0, 1, 5, 10, 20, 40))
p5 <- p5 + my_theme()
p5 <- p5 + labs(y = "Avg. detour")
p5

p6 <- ggplot(MILP_th[Approach %in% c("MILP", "MILP-threshold", "SP-threshold-DT")], aes(x = Approach, y = Ad.hoc.cost.prop, fill = Approach))
p6 <- p6 + geom_boxplot()
p6 <- p6 + scale_fill_brewer(palette="Set1")
p6 <- p6 + scale_x_discrete()
p6 <- p6 + my_theme()
p6 <- p6 + labs(y = "Proportion ad hoc cost")
p6



unq_exp <- unique(exp[, .(Net.size, Meters, Num.stores, Num.retailers, Cust.ret, Drv.ret)])

