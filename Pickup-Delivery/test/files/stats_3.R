library(data.table)
library(ggplot2)

# setwd("C:/Users/oscarcg/Documents/phd/code/Pickup-Delivery/test/files/final/")
setwd("./final")

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
      
      #legend.position      = "none",
      
      legend.background    = element_rect(fill = "white", size = 4, colour = "white"),
      legend.justification = c(1, 1),
      legend.position      = c(1, 1),
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

# BOUNDS EFFECT in LL-EP
# -------------
bds <- fread("LL-EP_bounds_32C_12Sep2019_030832.csv")
bds$Approach <- as.factor(bds$Approach)
bds$Zone <- as.factor(bds$Zone)
bds$Distribution <- as.factor(bds$Distribution)
bds$Bounds <- as.factor(bds$Bounds)

bds_prop_f <- function(sd) {
  baseline <- sd[Bounds == "lb", -1, with = FALSE]
  other <- sd[Bounds != "lb", -1, with = FALSE]
  if(nrow(baseline) == 1 & nrow(other) == 1){
    other[1] / baseline[1]
  }
}

sd_cols_bds <- c("Bounds", "Cost", "Elapsed.time")

bds_both_prop_dt <- bds[Approach == "LL-EP" & Bounds %in% c('both', 'lb') & Cost != -1, bds_prop_f(.SD), by = list(Seed, Limit), .SDcols = sd_cols_bds]
bds_both_prop_dt[, Bounds := "Both"]
bds_ub_prop_dt <- bds[Approach == "LL-EP" & Bounds %in% c('ub', 'lb') & Cost != -1, bds_prop_f(.SD), by = list(Seed, Limit), .SDcols = sd_cols_bds]
bds_ub_prop_dt[, Bounds := "Upper"]
bds_prop_dt <- rbind(bds_both_prop_dt, bds_ub_prop_dt)

p_bds_lb_cost_prop <- ggplot(bds_prop_dt, aes(x = Bounds, y = Cost)) 
p_bds_lb_cost_prop <- p_bds_lb_cost_prop + geom_boxplot() 
p_bds_lb_cost_prop <- p_bds_lb_cost_prop + scale_x_discrete()
p_bds_lb_cost_prop <- p_bds_lb_cost_prop + my_theme()
p_bds_lb_cost_prop <- p_bds_lb_cost_prop + labs(y = "Proportion Lower Bound Cost")
p_bds_lb_cost_prop

p_bds_lb_time_prop <- ggplot(bds_prop_dt, aes(x = Bounds, y = Elapsed.time)) 
p_bds_lb_time_prop <- p_bds_lb_time_prop + geom_boxplot() 
p_bds_lb_time_prop <- p_bds_lb_time_prop + scale_x_discrete()
p_bds_lb_time_prop <- p_bds_lb_time_prop + my_theme()
p_bds_lb_time_prop <- p_bds_lb_time_prop + labs(y = "Proportion Lower Bound processing time")
p_bds_lb_time_prop

# LL-EP (no limit) Vs MILP
# ------------------------
milp_12C <- fread("MILP_LL-EP_12C_11Sep2019_233258.csv")
milp_12C$Approach <- as.factor(milp_12C$Approach)
milp_12C$Zone <- as.factor(milp_12C$Zone)
milp_12C$Distribution <- as.factor(milp_12C$Distribution)
milp_12C$Bounds <- as.factor(milp_12C$Bounds)

milp_8C <- fread("MILP_LL-EP_8C_12Sep2019_131806.csv")
milp_8C$Approach <- as.factor(milp_8C$Approach)
milp_8C$Zone <- as.factor(milp_8C$Zone)
milp_8C$Distribution <- as.factor(milp_8C$Distribution)
milp_8C$Bounds <- as.factor(milp_8C$Bounds)

milp_prop_f <- function(sd) {
  baseline <- sd[Approach == "MILP", -1, with = FALSE]
  other <- sd[Approach != "MILP", -1, with = FALSE]
  if(nrow(baseline) == 1 & nrow(other) == 1){
    other[1] / baseline[1]
  }
}

sd_cols_milp <- c("Approach", "Cost", "Service.cost", "Elapsed.time")

milp_8C_prop_dt <- milp_8C[Cost != -1, milp_prop_f(.SD), by = Seed, .SDcols = sd_cols_milp]
milp_8C_prop_dt[, Customers := 8]
milp_12C_prop_dt <- milp_12C[Cost != -1, milp_prop_f(.SD), by = Seed, .SDcols = sd_cols_milp]
milp_12C_prop_dt[, Customers := 12]

milp_prop_dt <- rbind(milp_8C_prop_dt, milp_12C_prop_dt)
milp_prop_dt$Customers <- as.factor(milp_prop_dt$Customers)
milp_prop_dt[is.infinite(Service.cost), Service.cost := NaN]
milp_prop_dt[Service.cost > 1e6, Service.cost := NaN]
milp_prop_dt[Service.cost < 1e-6, Service.cost := NaN]

p_milp_cost_prop <- ggplot(milp_prop_dt, aes(x = Service.cost, fill = Customers, colour = Customers))
p_milp_cost_prop <- p_milp_cost_prop + geom_density(alpha = 0.1, adjust = 1/3)
p_milp_cost_prop <- p_milp_cost_prop + my_theme()
p_milp_cost_prop <- p_milp_cost_prop + labs(x = "Proportion MILP Service Cost")
p_milp_cost_prop

p_milp_time_prop <- ggplot(milp_prop_dt, aes(x = Elapsed.time, fill = Customers, colour = Customers))
p_milp_time_prop <- p_milp_time_prop + geom_density(alpha = 0.1, adjust = 1/3)
p_milp_time_prop <- p_milp_time_prop + my_theme()
p_milp_time_prop <- p_milp_time_prop + labs(x = "Proportion MILP Processing Time")
p_milp_time_prop


# LL-EP Vs Voronoi (32 Customers + Limits: [0, 2, 4, 8, 16] + no spatial partitioning)
# ------------------------------------------------------------------------------------
vor_32C <- fread("LL-EP_bounds_32C_12Sep2019_030832.csv")
vor_32C$Approach <- as.factor(vor_32C$Approach)
vor_32C$Zone <- as.factor(vor_32C$Zone)
vor_32C$Distribution <- as.factor(vor_32C$Distribution)
vor_32C$Bounds <- as.factor(vor_32C$Bounds)

vor_prop_f <- function(sd) {
  baseline <- sd[Approach == "SP-Voronoi", -1, with = FALSE]
  other <- sd[Approach != "SP-Voronoi", -1, with = FALSE]
  if(nrow(baseline) == 1 & nrow(other) == 1){
    other[1] / baseline[1]
  }
}

sd_cols_vor <- c("Approach", "Cost", "Service.cost",  "Elapsed.time", "Avg.detour")

vor_32C_lim0_prop_dt <- vor_32C[(Approach == 'SP-Voronoi' | (Approach == 'LL-EP' & Limit == 0)) &  Bounds == 'both' & Cost != -1, vor_prop_f(.SD), by = Seed, .SDcols = sd_cols_vor]
vor_32C_lim0_prop_dt[, Limit := 0]
vor_32C_lim2_prop_dt <- vor_32C[(Approach == 'SP-Voronoi' | (Approach == 'LL-EP' & Limit == 2)) &  Bounds == 'both' & Cost != -1, vor_prop_f(.SD), by = Seed, .SDcols = sd_cols_vor]
vor_32C_lim2_prop_dt[, Limit := 2]
vor_32C_lim4_prop_dt <- vor_32C[(Approach == 'SP-Voronoi' | (Approach == 'LL-EP' & Limit == 4)) &  Bounds == 'both' & Cost != -1, vor_prop_f(.SD), by = Seed, .SDcols = sd_cols_vor]
vor_32C_lim4_prop_dt[, Limit := 4]
vor_32C_lim8_prop_dt <- vor_32C[(Approach == 'SP-Voronoi' | (Approach == 'LL-EP' & Limit == 8)) &  Bounds == 'both' & Cost != -1, vor_prop_f(.SD), by = Seed, .SDcols = sd_cols_vor]
vor_32C_lim8_prop_dt[, Limit := 8]
vor_32C_lim16_prop_dt <- vor_32C[(Approach == 'SP-Voronoi' | (Approach == 'LL-EP' & Limit == 16)) &  Bounds == 'both' & Cost != -1, vor_prop_f(.SD), by = Seed, .SDcols = sd_cols_vor]
vor_32C_lim16_prop_dt[, Limit := 16]

vor_32C_prop_dt <- rbind(vor_32C_lim0_prop_dt, vor_32C_lim2_prop_dt, vor_32C_lim4_prop_dt, vor_32C_lim8_prop_dt, vor_32C_lim16_prop_dt)
vor_32C_prop_dt[, Limit := as.factor(Limit)]

p_vor_32C_cost_prop <- ggplot(vor_32C_prop_dt, aes(x = Limit, y = Service.cost, fill = Limit))
# p_vor_32C_cost_prop <- ggplot(vor_32C_prop_dt, aes(x = Service.cost, fill = Limit, colour = Limit)) 
p_vor_32C_cost_prop <- p_vor_32C_cost_prop + geom_boxplot()
# p_vor_32C_cost_prop <- p_vor_32C_cost_prop + geom_density(alpha = 0.1, adjust = 1/5)
p_vor_32C_cost_prop <- p_vor_32C_cost_prop + scale_x_discrete()
#p_vor_32C_cost_prop <- p_vor_32C_cost_prop + scale_y_log10()
#p_vor_32C_cost_prop <- p_vor_32C_cost_prop + my_theme()
p_vor_32C_cost_prop <- p_vor_32C_cost_prop + labs(y = "Proportion Voronoi Service Cost")
p_vor_32C_cost_prop

p_vor_32C_time_prop <- ggplot(vor_32C_prop_dt, aes(x = Limit, y = Elapsed.time, fill = Limit))
#p_vor_32C_time_prop <- ggplot(vor_32C_prop_dt, aes(x = Elapsed.time, fill = Limit, colour = Limit))
p_vor_32C_time_prop <- p_vor_32C_time_prop + geom_boxplot()
#p_vor_32C_time_prop <- p_vor_32C_time_prop + geom_density(alpha = 0.1, adjust = 1/5)
p_vor_32C_time_prop <- p_vor_32C_time_prop + scale_x_discrete()
p_vor_32C_time_prop <- p_vor_32C_time_prop + scale_y_log10()
#p_vor_32C_time_prop <- p_vor_32C_time_prop + my_theme()
p_vor_32C_time_prop <- p_vor_32C_time_prop + labs(y = "Proportion Voronoi Processing Time")
p_vor_32C_time_prop