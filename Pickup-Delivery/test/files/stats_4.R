library(data.table)
library(ggplot2)

setwd("C:/Users/oscarcg/Documents/phd/code/Pickup-Delivery/test/files/final/")
# setwd("./final")

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
      
      #legend.background    = element_rect(fill = "white", size = 4, colour = "white"),
      legend.background    = element_rect(color = "grey"),
      legend.justification = c(1, 0),
      #legend.position      = c(1, 0),
      #legend.title         = element_text(size = 9, lineheight = 0.9, colour = "black", hjust = 1, face="bold"),
      legend.title         = element_blank(),
      legend.text          = element_text(size = 8, lineheight = 0.9, colour = "black", hjust = 1),
      
      #legend.text           = element_text(size = 8, lineheight = 0.9, hjust = 1),
      #legend.title          = element_text(size = 9),
      
      # dark strips with light text (inverse contrast compared to theme_grey)
      strip.background = element_rect(fill = "grey70", colour = NA),
      strip.text       = element_text(colour = "white", size = rel(0.8)),
      
      #axis.title.x = axis_x_title,
      #axis.title.y = axis_y_title,
      axis.title.x = element_text(margin = margin(t = 5, r = 0, b = 0, l = 0), size = 8, vjust = 0.5, face="bold"),
      axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 8, angle = 90, vjust = 0.5, face="bold"),
      #axis.text    = element_text(size = 8, lineheight = 0.9, colour = "grey50", hjust = 1),
      axis.text    = element_text(size = 8, lineheight = 0.9, colour = "black", hjust = 1),
      
      complete = TRUE
    )
  
}


multiplot <- function(..., plotlist=NULL, file, cols=1, layout=NULL) {
  library(grid)
  
  # Make a list from the ... arguments and plotlist
  plots <- c(list(...), plotlist)
  
  numPlots = length(plots)
  
  # If layout is NULL, then use 'cols' to determine layout
  if (is.null(layout)) {
    # Make the panel
    # ncol: Number of columns of plots
    # nrow: Number of rows needed, calculated from # of cols
    layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
                     ncol = cols, nrow = ceiling(numPlots/cols))
  }
  
  if (numPlots==1) {
    print(plots[[1]])
    
  } else {
    # Set up the page
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))
    
    # Make each plot, in the correct location
    for (i in 1:numPlots) {
      # Get the i,j matrix positions of the regions that contain this subplot
      matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))
      
      print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row,
                                      layout.pos.col = matchidx$col))
    }
  }
}


# EFFECT OF THE SHORTEST INDEPENDENT-ROUTE DISTANCE
# -------------------------------------------------
ird <- fread("IRB.csv")
ird[, Assignment := as.factor(Assignment)]
ird[, Partition := as.factor(Partition)]
ird[, Routing := as.factor(Routing)]
ird[, Zone := as.factor(Zone)]
ird[, Customers := as.factor(Customers)]
ird[, Distribution := as.factor(Distribution)]

ird <- ird[Dedicated.cost == 0 & Cost != -1]

ird[Assignment == 'SP-Voronoi', Assignment := 'V']
ird[Assignment == 'LL-EP', Assignment := 'IRD']
ird[Routing == 'BB', Routing := 'BnB']
ird[, Approach := paste(Assignment, Routing, sep = "-")]
ird$Approach <- factor(ird$Approach, levels = c('V-NN', 'IRD-NN', 'V-BnB', 'IRD-BnB'))
ird[, Total.service.cost := Dedicated.cost + Service.cost]


p_ird_c <- ggplot(ird, aes(x = Customers, y = Total.service.cost, fill = Approach)) 
p_ird_c <- p_ird_c + geom_boxplot() 
p_ird_c <- p_ird_c + scale_x_discrete()
p_ird_c <- p_ird_c + scale_y_log10()
p_ird_c <- p_ird_c + my_theme()
p_ird_c <- p_ird_c + labs(y = "Service Cost")
p_ird_c

p_ird_t <- ggplot(ird, aes(x = Customers, y = Elapsed.time, fill = Approach)) 
p_ird_t <- p_ird_t + geom_boxplot() 
p_ird_t <- p_ird_t + scale_x_discrete()
p_ird_t <- p_ird_t + scale_y_log10()
p_ird_t

p_ird_d <- ggplot(ird, aes(x = Customers, y = Avg.detour, fill = Approach)) 
p_ird_d <- p_ird_d + geom_boxplot() 
p_ird_d <- p_ird_d + scale_x_discrete()
p_ird_d


# COMPARISON AGAINST MILP
# -----------------------
milp <- fread("MILP.csv")
milp[, Assignment := as.factor(Assignment)]
milp[, Partition := as.factor(Partition)]
milp[, Routing := as.factor(Routing)]
milp[, Zone := as.factor(Zone)]
milp[, Customers := as.factor(Customers)]
milp[, Distribution := as.factor(Distribution)]

milp <- milp[Customers %in% c(8, 12, 16)]
milp <- milp[Cost != -1]

milp[Assignment == 'LL-EP', Assignment := 'IRD']
milp[Routing == 'BB', Routing := 'BnB']
milp[Assignment == 'IRD', Approach := paste(Assignment, Routing, sep = "-")]
milp[Assignment == 'MILP', Approach := Assignment]
milp$Approach <- factor(milp$Approach, levels = c('MILP', 'IRD-BnB'))
milp[, Total.service.cost := Dedicated.cost + Service.cost]


milp_prop_f <- function(sd) {
  baseline <- sd[Approach == "MILP", -1, with = FALSE]
  other <- sd[Approach != "MILP", -1, with = FALSE]
  if(nrow(baseline) == 1 & nrow(other) == 1){
    other[1] / baseline[1]
  }
}

sd_cols_milp <- c("Approach", "Cost", "Service.cost", "Total.service.cost", "Elapsed.time")

milp_prop_dt <- milp[, milp_prop_f(.SD), by = list(Seed, Customers), .SDcols = sd_cols_milp]

p_milp_c <- ggplot(milp_prop_dt, aes(x = Customers, y = Total.service.cost)) 
p_milp_c <- p_milp_c + geom_boxplot() 
p_milp_c <- p_milp_c + scale_x_discrete()
p_milp_c <- p_milp_c + scale_y_continuous(breaks = c(1.0, 1.25, 1.5, 1.75, 2.0))
p_milp_c <- p_milp_c + geom_hline(yintercept=1.0, linetype="twodash", color = "red", size = 1)
p_milp_c <- p_milp_c + my_theme()
p_milp_c <- p_milp_c + labs(y = "Proportion MILP Service Cost")
p_milp_c

p_milp_t <- ggplot(milp_prop_dt, aes(x = Customers, y = Elapsed.time)) 
p_milp_t <- p_milp_t + geom_boxplot() 
p_milp_t <- p_milp_t + scale_x_discrete()
p_milp_t <- p_milp_t + scale_y_log10()
p_milp_t <- p_milp_t + my_theme()
p_milp_t <- p_milp_t + labs(y = "Proportion MILP Processing Time")
p_milp_t


# MAX LOADS
# ---------
lim <- fread("Limits_256C.csv")
lim[, Assignment := as.factor(Assignment)]
lim[, Partition := as.factor(Partition)]
lim[, Routing := as.factor(Routing)]
lim[, Zone := as.factor(Zone)]
lim[, Customers := as.factor(Customers)]
lim[, Distribution := as.factor(Distribution)]
lim[, Limit := as.factor(Limit)]

lim <- lim[Dedicated.cost == 0 & Cost != -1 & Limit %in% c(4, 6, 8, 10, 12)]

lim[Assignment == 'SP-Voronoi', Assignment := 'V']
lim[Assignment == 'LL-EP', Assignment := 'IRD']
lim[Routing == 'BB', Routing := 'BnB']
lim[, Approach := paste(Assignment, Routing, sep = "-")]
lim$Approach <- factor(lim$Approach, levels = c('V-NN', 'IRD-NN', 'V-BnB', 'IRD-BnB'))
lim[, Total.service.cost := Dedicated.cost + Service.cost]

p_lim_c <- ggplot(lim, aes(x = Limit, y = Total.service.cost, fill = Approach)) 
p_lim_c <- p_lim_c + geom_boxplot(color = "grey", alpha = 1/10)
p_lim_c <- p_lim_c + geom_smooth(method = "loess", se=FALSE, aes(group = Approach, color = Approach))
p_lim_c <- p_lim_c + scale_x_discrete()
p_lim_c <- p_lim_c + my_theme()
p_lim_c <- p_lim_c + labs(x = "Max. Degree m")
p_lim_c <- p_lim_c + labs(y = "Service Cost")
p_lim_c

p_lim_t <- ggplot(lim, aes(x = Limit, y = Elapsed.time, fill = Approach))
p_lim_t <- p_lim_t + geom_boxplot(color = "grey", alpha = 1/10) 
p_lim_t <- p_lim_t + geom_smooth(method = "loess", se=FALSE, aes(group = Approach, color = Approach))
p_lim_t <- p_lim_t + scale_x_discrete()
p_lim_t <- p_lim_t + scale_y_log10()
p_lim_t <- p_lim_t + my_theme()
p_lim_t <- p_lim_t + labs(x = "Max. Degree m")
p_lim_t <- p_lim_t + labs(y = "Processing Time")
p_lim_t

p_lim_d <- ggplot(lim, aes(x = Limit, y = Avg.detour, fill = Approach))
p_lim_d <- p_lim_d + geom_boxplot() 
p_lim_d <- p_lim_d + scale_x_discrete()
p_lim_d <- p_lim_d + scale_y_log10()
p_lim_d


# SPACE PARTITIONING
# ------------------
spar <- fread("Fr_Thr.csv")
spar[, Assignment := as.factor(Assignment)]
spar[, Partition := as.factor(Partition)]
spar[, Routing := as.factor(Routing)]
spar[, Zone := as.factor(Zone)]
spar[, Customers := as.factor(Customers)]
spar[, Distribution := as.factor(Distribution)]
spar[, Limit := as.factor(Limit)]
spar[, Parameter := as.factor(Parameter)]

spar <- spar[Cost != -1]

spar[Assignment == 'SP-Voronoi', Assignment := 'V']
spar[Assignment == 'LL-EP', Assignment := 'IRD']
spar[Routing == 'BB', Routing := 'BnB']
spar[, Approach := paste(Assignment, Routing, sep = "-")]
spar$Approach <- factor(spar$Approach, levels = c('V-NN', 'IRD-NN', 'V-BnB', 'IRD-BnB'))
spar[, Total.service.cost := Dedicated.cost + Service.cost]

p_spar_f_c <- ggplot(spar[Partition == 'SP-fraction'], aes(x = Parameter, y = Total.service.cost, fill = Approach))
p_spar_f_c <- p_spar_f_c + geom_boxplot()
p_spar_f_c <- p_spar_f_c + scale_x_discrete()
#p_lim_c <- p_lim_c + scale_y_log10()
p_spar_f_c <- p_spar_f_c + my_theme()
p_spar_f_c <- p_spar_f_c + labs(x = "Fraction f")
p_spar_f_c <- p_spar_f_c + labs(y = "Service Cost")
p_spar_f_c

p_spar_f_t <- ggplot(spar[Partition == 'SP-fraction'], aes(x = Parameter, y = Elapsed.time, fill = Approach))
p_spar_f_t <- p_spar_f_t + geom_boxplot()
p_spar_f_t <- p_spar_f_t + scale_x_discrete()
p_spar_f_t <- p_spar_f_t + scale_y_log10()
p_spar_f_t <- p_spar_f_t + my_theme()
p_spar_f_t <- p_spar_f_t + labs(x = "Fraction f")
p_spar_f_t <- p_spar_f_t + labs(y = "Processing Time")
p_spar_f_t

p_spar_f_d <- ggplot(spar[Partition == 'SP-fraction'], aes(x = Parameter, y = Avg.detour, fill = Approach))
p_spar_f_d <- p_spar_f_d + geom_boxplot()
p_spar_f_d <- p_spar_f_d + scale_x_discrete()
#p_spar_d <- p_spar_d + scale_y_log10()
p_spar_f_d <- p_spar_f_d + my_theme()
p_spar_f_d <- p_spar_f_d + labs(x = "Fraction f")
p_spar_f_d <- p_spar_f_d + labs(y = "Average Detour")
p_spar_f_d

p_spar_f_sc <- ggplot(spar[Partition == 'SP-fraction'], aes(x = Parameter, y = Served, fill = Approach))
p_spar_f_sc <- p_spar_f_sc + geom_boxplot()
p_spar_f_sc <- p_spar_f_sc + scale_x_discrete()
#p_spar_d <- p_spar_d + scale_y_log10()
p_spar_f_sc <- p_spar_f_sc + my_theme()
p_spar_f_sc <- p_spar_f_sc + labs(x = "Fraction f")
p_spar_f_sc <- p_spar_f_sc + labs(y = "Served Customers")
p_spar_f_sc


multiplot(p_spar_f_c, p_spar_f_t, p_spar_f_d, p_spar_f_sc, cols = 4)


p_spar_c <- ggplot(spar[Partition == 'SP-threshold'], aes(x = Parameter, y = Total.service.cost, fill = Approach))
p_spar_c <- p_spar_c + geom_boxplot()
p_spar_c <- p_spar_c + scale_x_discrete()
#p_lim_c <- p_lim_c + scale_y_log10()
p_spar_c <- p_spar_c + my_theme()
p_spar_c <- p_spar_c + labs(x = "Threshold t")
p_spar_c <- p_spar_c + labs(y = "Service Cost")
p_spar_c

p_spar_t <- ggplot(spar[Partition == 'SP-threshold'], aes(x = Parameter, y = Elapsed.time, fill = Approach))
p_spar_t <- p_spar_t + geom_boxplot()
p_spar_t <- p_spar_t + scale_x_discrete()
p_spar_t <- p_spar_t + scale_y_log10()
p_spar_t <- p_spar_t + my_theme()
p_spar_t <- p_spar_t + labs(x = "Threshold t")
p_spar_t <- p_spar_t + labs(y = "Processing Time")
p_spar_t

p_spar_d <- ggplot(spar[Partition == 'SP-threshold'], aes(x = Parameter, y = Avg.detour, fill = Approach))
p_spar_d <- p_spar_d + geom_boxplot()
p_spar_d <- p_spar_d + scale_x_discrete()
#p_spar_d <- p_spar_d + scale_y_log10()
p_spar_d <- p_spar_d + my_theme()
p_spar_d <- p_spar_d + labs(x = "Threshold t")
p_spar_d <- p_spar_d + labs(y = "Average Detour")
p_spar_d

p_spar_sc <- ggplot(spar[Partition == 'SP-threshold'], aes(x = Parameter, y = Served, fill = Approach))
p_spar_sc <- p_spar_sc + geom_boxplot()
p_spar_sc <- p_spar_sc + scale_x_discrete()
#p_spar_d <- p_spar_d + scale_y_log10()
p_spar_sc <- p_spar_sc + my_theme()
p_spar_sc <- p_spar_sc + labs(x = "Threshold t")
p_spar_sc <- p_spar_sc + labs(y = "Served Customers")
p_spar_sc

