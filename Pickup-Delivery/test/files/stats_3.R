library(data.table)
library(ggplot2)

setwd("C:/Users/oscarcg/Documents/phd/code/Pickup-Delivery/test/files/final/")

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
bds <- fread("LL-EP_bounds_12Sep2019_030832.csv")
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

milp_prop_f <- function(sd) {
  baseline <- sd[Approach == "MILP", -1, with = FALSE]
  other <- sd[Approach != "MILP", -1, with = FALSE]
  if(nrow(baseline) == 1 & nrow(other) == 1){
    other[1] / baseline[1]
  }
}

sd_cols_milp <- c("Approach", "Cost", "Elapsed.time")

milp_12C_prop_dt <- milp_12C[Cost != -1, milp_prop_f(.SD), by = Seed, .SDcols = sd_cols_milp]
milp_12C_prop_dt[, Customers := 12]

milp_prop_dt <- rbind(milp_12C_prop_dt)

p_milp_cost_prop <- ggplot(milp_prop_dt, aes(x = Cost, fill = Customers, colour = Customers)) 
p_milp_cost_prop <- p_milp_cost_prop + geom_density(alpha = 0.1, adjust = 1/5)
p_milp_cost_prop <- p_milp_cost_prop + my_theme()
p_milp_cost_prop <- p_milp_cost_prop + labs(x = "Proportion MILP Cost")
p_milp_cost_prop

p_milp_time_prop <- ggplot(milp_prop_dt, aes(x = Elapsed.time, fill = Customers, colour = Customers)) 
p_milp_time_prop <- p_milp_time_prop + geom_density(alpha = 0.1, adjust = 1/5)
p_milp_time_prop <- p_milp_time_prop + my_theme()
p_milp_time_prop <- p_milp_time_prop + labs(x = "Proportion MILP processing time")
p_milp_time_prop