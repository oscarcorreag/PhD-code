library(data.table)
library(ggplot2)

setwd("C:/Users/oscarcg/Documents/phd/code/Pickup-Delivery/test/files/final/")
# setwd("../Pickup-Delivery/test/files.final/")

my_theme_11 <- function(base_size = 11, base_family = "") {
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
      
      #legend.background    = element_rect(fill = "white", size = 4, colour = "white"),
      legend.background    = element_rect(color = "grey"),
      legend.justification = c(1, 1),
      legend.position      = c(1, 1),
      legend.title         = element_text(size = 11, lineheight = 0.9, colour = "black", hjust = 1, face="bold"),
      #legend.title         = element_blank(),
      legend.text          = element_text(size = 11, lineheight = 0.9, colour = "black", hjust = 1),
      
      #legend.text           = element_text(size = 8, lineheight = 0.9, hjust = 1),
      #legend.title          = element_text(size = 9),
      
      # dark strips with light text (inverse contrast compared to theme_grey)
      strip.background = element_rect(fill = "grey70", colour = NA),
      strip.text       = element_text(colour = "white", size = rel(0.8)),
      
      #axis.title.x = axis_x_title,
      #axis.title.y = axis_y_title,
      #axis.title.x = element_text(margin = margin(t = 5, r = 0, b = 0, l = 0), size = 12, vjust = 0.5, face="bold"),
      axis.title.x = element_text(margin = margin(t = 5, r = 0, b = 0, l = 0), size = 10, vjust = 0.5),
      #axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 12, angle = 90, vjust = 0.5, face="bold"),
      axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 10, angle = 90, vjust = 0.5),
      #axis.text    = element_text(size = 8, lineheight = 0.9, colour = "grey50", hjust = 1),
      axis.text    = element_text(size = 10, lineheight = 0.9, colour = "black", hjust = 1),
      
      complete = TRUE
    )
  
}

my_theme_10 <- function(base_size = 11, base_family = "") {
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
      
      #legend.background    = element_rect(fill = "white", size = 4, colour = "white"),
      legend.background    = element_rect(color = "grey"),
      legend.justification = c(1, 0),
      legend.position      = c(1, 0),
      #legend.title         = element_text(size = 9, lineheight = 0.9, colour = "black", hjust = 1, face="bold"),
      legend.title         = element_blank(),
      legend.text          = element_text(size = 11, lineheight = 0.9, colour = "black", hjust = 1),
      
      #legend.text           = element_text(size = 8, lineheight = 0.9, hjust = 1),
      #legend.title          = element_text(size = 9),
      
      # dark strips with light text (inverse contrast compared to theme_grey)
      strip.background = element_rect(fill = "grey70", colour = NA),
      strip.text       = element_text(colour = "white", size = rel(0.8)),
      
      #axis.title.x = axis_x_title,
      #axis.title.y = axis_y_title,
      #axis.title.x = element_text(margin = margin(t = 5, r = 0, b = 0, l = 0), size = 9, vjust = 0.5, face="bold"),
      axis.title.x = element_text(margin = margin(t = 5, r = 0, b = 0, l = 0), size = 12, vjust = 0.5),
      #axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 9, angle = 90, vjust = 0.5, face="bold"),
      axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 12, angle = 90, vjust = 0.5),
      #axis.text    = element_text(size = 8, lineheight = 0.9, colour = "grey50", hjust = 1),
      axis.text    = element_text(size = 10, lineheight = 0.9, colour = "black", hjust = 1),
      
      complete = TRUE
    )
  
}

my_theme_01 <- function(base_size = 11, base_family = "") {
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
      
      #legend.background    = element_rect(fill = "white", size = 4, colour = "white"),
      legend.background    = element_rect(color = "grey"),
      legend.justification = c(0, 1),
      legend.position      = c(0, 1),
      #legend.title         = element_text(size = 9, lineheight = 0.9, colour = "black", hjust = 1, face="bold"),
      legend.title         = element_blank(),
      legend.text          = element_text(size = 11, lineheight = 0.9, colour = "black", hjust = 1),
      
      #legend.text           = element_text(size = 8, lineheight = 0.9, hjust = 1),
      #legend.title          = element_text(size = 9),
      
      # dark strips with light text (inverse contrast compared to theme_grey)
      strip.background = element_rect(fill = "grey70", colour = NA),
      strip.text       = element_text(colour = "white", size = rel(0.8)),
      
      #axis.title.x = axis_x_title,
      #axis.title.y = axis_y_title,
      #axis.title.x = element_text(margin = margin(t = 5, r = 0, b = 0, l = 0), size = 12, vjust = 0.5, face="bold"),
      axis.title.x = element_text(margin = margin(t = 5, r = 0, b = 0, l = 0), size = 10, vjust = 0.5),
      #axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 12, angle = 90, vjust = 0.5, face="bold"),
      axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 10, angle = 90, vjust = 0.5),
      #axis.text    = element_text(size = 8, lineheight = 0.9, colour = "grey50", hjust = 1),
      axis.text    = element_text(size = 10, lineheight = 0.9, colour = "black", hjust = 1),
      
      complete = TRUE
    )
  
}

my_theme_00 <- function(base_size = 11, base_family = "") {
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
      
      #legend.background    = element_rect(fill = "white", size = 4, colour = "white"),
      legend.background    = element_rect(color = "grey"),
      legend.justification = c(0, 0),
      legend.position      = c(0, 0),
      #legend.title         = element_text(size = 9, lineheight = 0.9, colour = "black", hjust = 1, face="bold"),
      legend.title         = element_blank(),
      legend.text          = element_text(size = 11, lineheight = 0.9, colour = "black", hjust = 1),
      
      #legend.text           = element_text(size = 8, lineheight = 0.9, hjust = 1),
      #legend.title          = element_text(size = 9),
      
      # dark strips with light text (inverse contrast compared to theme_grey)
      strip.background = element_rect(fill = "grey70", colour = NA),
      strip.text       = element_text(colour = "white", size = rel(0.8)),
      
      #axis.title.x = axis_x_title,
      #axis.title.y = axis_y_title,
      #axis.title.x = element_text(margin = margin(t = 5, r = 0, b = 0, l = 0), size = 9, vjust = 0.5, face="bold"),
      axis.title.x = element_text(margin = margin(t = 5, r = 0, b = 0, l = 0), size = 12, vjust = 0.5),
      #axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 9, angle = 90, vjust = 0.5, face="bold"),
      axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 12, angle = 90, vjust = 0.5),
      #axis.text    = element_text(size = 8, lineheight = 0.9, colour = "grey50", hjust = 1),
      axis.text    = element_text(size = 10, lineheight = 0.9, colour = "black", hjust = 1),
      
      complete = TRUE
    )
  
}

my_theme_none <- function(base_size = 11, base_family = "") {
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
      legend.justification = c(1, 1),
      #legend.position      = c(1, 1),
      #legend.title         = element_text(size = 9, lineheight = 0.9, colour = "black", hjust = 1, face="bold"),
      legend.title         = element_blank(),
      legend.text          = element_text(size = 11, lineheight = 0.9, colour = "black", hjust = 1),
      
      #legend.text           = element_text(size = 8, lineheight = 0.9, hjust = 1),
      #legend.title          = element_text(size = 9),
      
      # dark strips with light text (inverse contrast compared to theme_grey)
      strip.background = element_rect(fill = "grey70", colour = NA),
      strip.text       = element_text(colour = "white", size = rel(0.8)),
      
      #axis.title.x = axis_x_title,
      #axis.title.y = axis_y_title,
      #axis.title.x = element_text(margin = margin(t = 5, r = 0, b = 0, l = 0), size = 12, vjust = 0.5, face="bold"),
      axis.title.x = element_text(margin = margin(t = 5, r = 0, b = 0, l = 0), size = 10, vjust = 0.5),
      #axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 12, angle = 90, vjust = 0.5, face="bold"),
      axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 10, angle = 90, vjust = 0.5),
      #axis.text    = element_text(size = 8, lineheight = 0.9, colour = "grey50", hjust = 1),
      axis.text    = element_text(size = 10, lineheight = 0.9, colour = "black", hjust = 1),
      
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


# EFFECT OF MAX. DEGREE m
# -----------------------
lim <- fread("Degree.csv")
lim[, Assignment := as.factor(Assignment)]
lim[, Partition := as.factor(Partition)]
lim[, Routing := as.factor(Routing)]
lim[, Zone := as.factor(Zone)]
lim[, Customers := as.factor(Customers)]
lim[, Ratio := as.factor(Ratio)]
lim[, Distribution := as.factor(Distribution)]
lim[, Limit := as.factor(Limit)]
lim[, Parameter := as.factor(Parameter)]

lim <- lim[Dedicated.cost == 0 & Cost != -1 & Limit %in% c(4, 6, 8, 10, 12)]

lim[Assignment == 'SP-Voronoi', Assignment := 'NN']
lim[Assignment == 'LL-EP', Assignment := 'IRNN']
lim[Routing == 'BB', Routing := 'BnB']
lim[, Approach := paste(Assignment, Routing, sep = "-")]
lim$Approach <- factor(lim$Approach, levels = c('NN-NN', 'IRNN-NN', 'NN-BnB', 'IRNN-BnB'))
lim[, Total.service.cost := Dedicated.cost + Service.cost]

# lab1 <- c(expression(dist[ra]-NN), expression(dist[ra]-BnB))
# lab1 <- c(expression(dist[IR]-BnB))

# p_lim_c <- ggplot(lim, aes(x = Limit, y = Total.service.cost, fill = Approach))
p_lim_c <- ggplot(lim[Approach == 'IRNN-BnB'], aes(x = Limit, y = Total.service.cost, fill = Approach))
p_lim_c <- p_lim_c + geom_boxplot(color = "grey", alpha = 1/10)
p_lim_c <- p_lim_c + geom_smooth(method = "loess", se=FALSE, aes(group = Approach, color = Approach))
p_lim_c <- p_lim_c + scale_x_discrete()
p_lim_c <- p_lim_c + my_theme_11()
# p_lim_c <- p_lim_c + scale_fill_manual(values = c("#D55E00", "#56B4E9"), labels = lab1)
# p_lim_c <- p_lim_c + scale_color_manual(values = c("#D55E00", "#56B4E9"), labels= lab1)
p_lim_c <- p_lim_c + scale_fill_manual(values = c("#56B4E9"))
p_lim_c <- p_lim_c + scale_color_manual(values = c("#56B4E9"))
p_lim_c <- p_lim_c + labs(x = "Max. Degree m")
p_lim_c <- p_lim_c + labs(y = "Service Cost (m)")
p_lim_c

# p_lim_t <- ggplot(lim, aes(x = Limit, y = Elapsed.time, fill = Approach))
p_lim_t <- ggplot(lim[Approach == 'IRNN-BnB'], aes(x = Limit, y = Elapsed.time, fill = Approach))
p_lim_t <- p_lim_t + geom_boxplot(color = "grey", alpha = 1/10) 
p_lim_t <- p_lim_t + geom_smooth(method = "loess", se=FALSE, aes(group = Approach, color = Approach))
p_lim_t <- p_lim_t + scale_x_discrete()
p_lim_t <- p_lim_t + scale_y_log10()
p_lim_t <- p_lim_t + my_theme_none()
# p_lim_t <- p_lim_t + scale_fill_manual(values = c("#D55E00", "#56B4E9"), labels = lab1)
# p_lim_t <- p_lim_t + scale_color_manual(values = c("#D55E00", "#56B4E9"), labels = lab1)
p_lim_t <- p_lim_t + scale_fill_manual(values = c("#56B4E9"))
p_lim_t <- p_lim_t + scale_color_manual(values = c("#56B4E9"))
p_lim_t <- p_lim_t + labs(x = "Max. Degree m")
p_lim_t <- p_lim_t + labs(y = "Processing Time (s)")
p_lim_t

multiplot(p_lim_c, p_lim_t, cols = 2)


# EFFECT OF THE SHORTEST INDEPENDENT-ROUTE DISTANCE
# -------------------------------------------------
ird <- fread("Customers.csv")
ird[, Assignment := as.factor(Assignment)]
ird[, Partition := as.factor(Partition)]
ird[, Routing := as.factor(Routing)]
ird[, Zone := as.factor(Zone)]
ird[, Customers := as.factor(Customers)]
ird[, Ratio := as.factor(Ratio)]
ird[, Distribution := as.factor(Distribution)]
ird[, Limit := as.factor(Limit)]
ird[, Parameter := as.factor(Parameter)]

ird <- ird[Dedicated.cost == 0 & Cost != -1]

ird[Assignment == 'SP-Voronoi', Assignment := 'NN']
ird[Assignment == 'LL-EP', Assignment := 'IRNN']
ird[Routing == 'BB', Routing := 'BnB']
ird[, Approach := paste(Assignment, Routing, sep = "-")]
ird$Approach <- factor(ird$Approach, levels = c('NN-NN', 'IRNN-NN', 'NN-BnB', 'IRNN-BnB'))
ird[, Total.service.cost := Dedicated.cost + Service.cost]

#p_ird_c <- ggplot(ird, aes(x = Customers, y = Total.service.cost, fill = Approach)) 
#p_ird_c <- p_ird_c + geom_boxplot() 
#p_ird_c <- p_ird_c + scale_x_discrete()
#p_ird_c <- p_ird_c + scale_y_log10()
#p_ird_c <- p_ird_c + my_theme_10()
#p_ird_c <- p_ird_c + scale_fill_manual(values = c("#F0E442", "#D55E00", "#009E73", "#56B4E9"))
#p_ird_c <- p_ird_c + labs(y = "Service Cost (m)")
#p_ird_c

ird_prop_f <- function(sd) {
  baseline <- sd[Assignment == "NN", -1, with = FALSE]
  other <- sd[Assignment == "IRNN", -1, with = FALSE]
  if(nrow(baseline) == 1 & nrow(other) == 1){
    other[1] / baseline[1]
  }
}

sd_cols_ird <- c("Assignment", "Cost", "Service.cost", "Total.service.cost")

ird_prop_dt <- ird[, ird_prop_f(.SD), by = list(Seed, Customers, Routing), .SDcols = sd_cols_ird]

p_ird_prop_c <- ggplot(ird_prop_dt, aes(x = Customers, y = Total.service.cost, fill = Routing)) 
p_ird_prop_c <- p_ird_prop_c + geom_boxplot() 
p_ird_prop_c <- p_ird_prop_c + scale_x_discrete()
p_ird_prop_c <- p_ird_prop_c + scale_y_continuous(breaks = c(.3, .5, .6, .9, 1.2, 1.5))
p_ird_prop_c <- p_ird_prop_c + geom_hline(yintercept=0.5, linetype="twodash", color = "red", size = 1)
p_ird_prop_c <- p_ird_prop_c + my_theme_11()
p_ird_prop_c <- p_ird_prop_c + scale_fill_manual(values = c("cyan", "green"))
# p_ird_prop_c <- p_ird_prop_c + labs(y = expression(atop("Prop. of Path-Generator", paste("Voronoi-based Service Cost"))))
p_ird_prop_c <- p_ird_prop_c + labs(y = "Prop. of NN-based assignment Service Cost")
p_ird_prop_c


#ird_r_prop_dt <- ird_r[, ird_prop_f(.SD), by = list(Seed, Ratio, Routing), .SDcols = sd_cols_ird]

#p_ird_r_prop_c <- ggplot(ird_r_prop_dt, aes(x = Ratio, y = Total.service.cost, fill = Routing)) 
#p_ird_r_prop_c <- p_ird_r_prop_c + geom_boxplot() 
#p_ird_r_prop_c <- p_ird_r_prop_c + scale_x_discrete()
#p_ird_r_prop_c <- p_ird_r_prop_c + geom_hline(yintercept=1.0, linetype="twodash", color = "red", size = 1)
#p_ird_r_prop_c <- p_ird_r_prop_c + my_theme_11()
#p_ird_r_prop_c <- p_ird_r_prop_c + labs(y = "Times Voronoi Service Cost")
#p_ird_r_prop_c

p_ird_t <- ggplot(ird, aes(x = Customers, y = Elapsed.time, fill = Approach)) 
p_ird_t <- p_ird_t + geom_boxplot() 
p_ird_t <- p_ird_t + scale_x_discrete()
p_ird_t <- p_ird_t + scale_y_log10(breaks = c(1e-01, 1, 1e+01, 1e+02, 1e+03))
p_ird_t <- p_ird_t + my_theme_10()
p_ird_t <- p_ird_t + scale_fill_manual(values = c("#F0E442", "#D55E00", "#009E73", "#56B4E9"))
p_ird_t <- p_ird_t + labs(y = "Elapsed time (s)")
p_ird_t

multiplot(p_ird_prop_c, p_ird_t, cols = 1)


ird_r <- fread("Ratios.csv")
ird_r[, Assignment := as.factor(Assignment)]
ird_r[, Partition := as.factor(Partition)]
ird_r[, Routing := as.factor(Routing)]
ird_r[, Zone := as.factor(Zone)]
ird_r[, Customers := as.factor(Customers)]
ird_r[, Ratio := as.factor(Ratio)]
ird_r[, Distribution := as.factor(Distribution)]
ird_r[, Limit := as.factor(Limit)]
ird_r[, Parameter := as.factor(Parameter)]

ird_r <- ird_r[Cost != -1]

ird_r[Assignment == 'SP-Voronoi', Assignment := 'NN']
ird_r[Assignment == 'LL-EP', Assignment := 'IRNN']
ird_r[Routing == 'BB', Routing := 'BnB']
ird_r[, Approach := paste(Assignment, Routing, sep = "-")]
ird_r$Approach <- factor(ird_r$Approach, levels = c('NN-NN', 'IRNN-NN', 'NN-BnB', 'IRNN-BnB'))
ird_r[, Total.service.cost := Dedicated.cost + Service.cost]

#p_ird_r_c <- ggplot(ird_r, aes(x = Ratio, y = Total.service.cost, fill = Approach)) 
#p_ird_r_c <- p_ird_r_c + geom_boxplot() 
#p_ird_r_c <- p_ird_r_c + scale_x_discrete()
#p_ird_r_c <- p_ird_r_c + my_theme_none()
#p_ird_r_c <- p_ird_r_c + scale_fill_manual(values = c("#F0E442", "#D55E00", "#009E73", "#56B4E9"))
#p_ird_r_c <- p_ird_r_c + labs(x = "Ratio customers / drivers")
#p_ird_r_c <- p_ird_r_c + labs(y = "Service Cost (m)")
#p_ird_r_c

#multiplot(p_ird_c, p_ird_r_c, cols = 1)


# lab1 <- c(expression(V-NN), expression(dist[ra]-NN), expression(V-BnB), expression(dist[ra]-BnB))

p_ird_r_d <- ggplot(ird_r, aes(x = Ratio, y = Avg.detour, fill = Approach)) 
p_ird_r_d <- p_ird_r_d + geom_boxplot() 
p_ird_r_d <- p_ird_r_d + scale_x_discrete()
p_ird_r_d <- p_ird_r_d + my_theme_01()
p_ird_r_d <- p_ird_r_d + theme(axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 10, angle = 90, vjust = 0.5))
# p_ird_r_d <- p_ird_r_d + scale_fill_manual(values = c("#F0E442", "#D55E00", "#009E73", "#56B4E9"), labels = lab1)
p_ird_r_d <- p_ird_r_d + scale_fill_manual(values = c("#F0E442", "#D55E00", "#009E73", "#56B4E9"))
p_ird_r_d <- p_ird_r_d + labs(x = "Ratio customers / drivers")
# p_ird_r_d <- p_ird_r_d + labs(y = paste("Avg. Detour (times", expression(k^+k^-), "original distance)"))
p_ird_r_d <- p_ird_r_d + labs(y = bquote("Avg. Detour (times " ~ k^"+" ~ k^"-" ~ " route's distance)"))
p_ird_r_d



# COMPARISON AGAINST MILP
# -----------------------
milp <- fread("MILP.csv")
milp[, Assignment := as.factor(Assignment)]
milp[, Partition := as.factor(Partition)]
milp[, Routing := as.factor(Routing)]
milp[, Zone := as.factor(Zone)]
milp[, Customers := as.factor(Customers)]
milp[, Ratio := as.factor(Ratio)]
milp[, Distribution := as.factor(Distribution)]
milp[, Limit := as.factor(Limit)]
milp[, Parameter := as.factor(Parameter)]

milp <- milp[Customers %in% c(8, 12, 16)]
milp <- milp[Cost != -1]

milp[Assignment == 'LL-EP', Assignment := 'IRNN']
milp[Routing == 'BB', Routing := 'BnB']
milp[Assignment == 'IRNN', Approach := paste(Assignment, Routing, sep = "-")]
milp[Assignment == 'MILP', Approach := Assignment]
milp$Approach <- factor(milp$Approach, levels = c('MILP', 'IRNN-BnB'))
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
p_milp_c <- p_milp_c + geom_boxplot(fill = "#56B4E9") 
p_milp_c <- p_milp_c + scale_x_discrete()
p_milp_c <- p_milp_c + scale_y_continuous(breaks = c(1.0, 1.25, 1.5, 1.75, 2.0))
p_milp_c <- p_milp_c + geom_hline(yintercept=1.5, linetype="twodash", color = "red", size = 1)
p_milp_c <- p_milp_c + my_theme_none()
p_milp_c <- p_milp_c + labs(y = "Prop. of MILP Service Cost")
p_milp_c

p_milp_t <- ggplot(milp_prop_dt, aes(x = Customers, y = Elapsed.time)) 
p_milp_t <- p_milp_t + geom_boxplot(fill = "#56B4E9") 
p_milp_t <- p_milp_t + scale_x_discrete()
p_milp_t <- p_milp_t + scale_y_log10(breaks = c(1, 1e-1, 1e-2, 1e-3))
p_milp_t <- p_milp_t + geom_hline(yintercept=1e-3, linetype="twodash", color = "red", size = 1)
p_milp_t <- p_milp_t + my_theme_none()
p_milp_t <- p_milp_t + labs(y = "Prop. of MILP Processing Time")
p_milp_t

multiplot(p_milp_c, p_milp_t, cols = 2)


# SPACE PARTITIONING
# ------------------
spar <- fread("Fr_Thr.csv")
spar[, Assignment := as.factor(Assignment)]
spar[, Partition := as.factor(Partition)]
spar[, Routing := as.factor(Routing)]
spar[, Zone := as.factor(Zone)]
spar[, Prop.served := Served / Customers]
spar[, Customers := as.factor(Customers)]
spar[, Ratio := as.factor(Ratio)]
spar[, Distribution := as.factor(Distribution)]
spar[, Limit := as.factor(Limit)]
spar[, Parameter := as.factor(Parameter)]

spar <- spar[Cost != -1]

spar[Assignment == 'SP-Voronoi', Assignment := 'NN']
spar[Assignment == 'LL-EP', Assignment := 'IRNN']
spar[Routing == 'BB', Routing := 'BnB']
spar[, Approach := paste(Assignment, Routing, sep = "-")]
spar$Approach <- factor(spar$Approach, levels = c('NN-NN', 'IRNN-NN', 'NN-BnB', 'IRNN-BnB'))
spar[, Total.service.cost := Dedicated.cost + Service.cost]

p_spar_f_c <- ggplot(spar[Partition == 'SP-fraction'], aes(x = Parameter, y = Total.service.cost, fill = Approach))
p_spar_f_c <- p_spar_f_c + geom_boxplot()
p_spar_f_c <- p_spar_f_c + scale_x_discrete()
p_spar_f_c <- p_spar_f_c + my_theme_none()
p_spar_f_c <- p_spar_f_c + scale_fill_manual(values = c("#F0E442", "#D55E00", "#009E73", "#56B4E9"))
p_spar_f_c <- p_spar_f_c + labs(x = "Fraction f")
p_spar_f_c <- p_spar_f_c + labs(y = "Service Cost (m)")
p_spar_f_c

p_spar_f_t <- ggplot(spar[Partition == 'SP-fraction'], aes(x = Parameter, y = Elapsed.time, fill = Approach))
p_spar_f_t <- p_spar_f_t + geom_boxplot()
p_spar_f_t <- p_spar_f_t + scale_x_discrete()
p_spar_f_t <- p_spar_f_t + scale_y_log10()
p_spar_f_t <- p_spar_f_t + my_theme_none()
p_spar_f_t <- p_spar_f_t + scale_fill_manual(values = c("#F0E442", "#D55E00", "#009E73", "#56B4E9"))
p_spar_f_t <- p_spar_f_t + labs(x = "Fraction f")
p_spar_f_t <- p_spar_f_t + labs(y = "Processing Time (s)")
p_spar_f_t

p_spar_f_d <- ggplot(spar[Partition == 'SP-fraction'], aes(x = Parameter, y = Avg.detour, fill = Approach))
p_spar_f_d <- p_spar_f_d + geom_boxplot()
p_spar_f_d <- p_spar_f_d + scale_x_discrete()
p_spar_f_d <- p_spar_f_d + my_theme_none()
p_spar_f_d <- p_spar_f_d + theme(axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 10, angle = 90, vjust = 0.5))
p_spar_f_d <- p_spar_f_d + scale_fill_manual(values = c("#F0E442", "#D55E00", "#009E73", "#56B4E9"))
p_spar_f_d <- p_spar_f_d + labs(x = "Fraction f")
p_spar_f_d <- p_spar_f_d + labs(y = bquote("Avg. Detour (times " ~ k^"+" ~ k^"-" ~ " route's distance)"))
p_spar_f_d

p_spar_f_sc <- ggplot(spar[Partition == 'SP-fraction'], aes(x = Parameter, y = Prop.served, fill = Approach))
p_spar_f_sc <- p_spar_f_sc + geom_boxplot()
p_spar_f_sc <- p_spar_f_sc + scale_x_discrete()
p_spar_f_sc <- p_spar_f_sc + my_theme_none()
p_spar_f_sc <- p_spar_f_sc + scale_fill_manual(values = c("#F0E442", "#D55E00", "#009E73", "#56B4E9"))
p_spar_f_sc <- p_spar_f_sc + labs(x = "Fraction f")
p_spar_f_sc <- p_spar_f_sc + labs(y = "Prop. Served Customers")
p_spar_f_sc

p_spar_c <- ggplot(spar[Partition == 'SP-threshold'], aes(x = Parameter, y = Total.service.cost, fill = Approach))
p_spar_c <- p_spar_c + geom_boxplot()
p_spar_c <- p_spar_c + scale_x_discrete()
p_spar_c <- p_spar_c + my_theme_none()
p_spar_c <- p_spar_c + scale_fill_manual(values = c("#F0E442", "#D55E00", "#009E73", "#56B4E9"))
p_spar_c <- p_spar_c + labs(x = "Threshold t")
p_spar_c <- p_spar_c + labs(y = "Service Cost (m)")
p_spar_c

p_spar_t <- ggplot(spar[Partition == 'SP-threshold'], aes(x = Parameter, y = Elapsed.time, fill = Approach))
p_spar_t <- p_spar_t + geom_boxplot()
p_spar_t <- p_spar_t + scale_x_discrete()
p_spar_t <- p_spar_t + scale_y_log10()
p_spar_t <- p_spar_t + my_theme_none()
p_spar_t <- p_spar_t + scale_fill_manual(values = c("#F0E442", "#D55E00", "#009E73", "#56B4E9"))
p_spar_t <- p_spar_t + labs(x = "Threshold t")
p_spar_t <- p_spar_t + labs(y = "Processing Time (s)")
p_spar_t

p_spar_d <- ggplot(spar[Partition == 'SP-threshold'], aes(x = Parameter, y = Avg.detour, fill = Approach))
p_spar_d <- p_spar_d + geom_boxplot()
p_spar_d <- p_spar_d + scale_x_discrete()
p_spar_d <- p_spar_d + my_theme_none()
p_spar_d <- p_spar_d + theme(axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 10, angle = 90, vjust = 0.5))
p_spar_d <- p_spar_d + scale_fill_manual(values = c("#F0E442", "#D55E00", "#009E73", "#56B4E9"))
p_spar_d <- p_spar_d + labs(x = "Threshold t")
p_spar_d <- p_spar_d + labs(y = bquote("Avg. Detour (times " ~ k^"+" ~ k^"-" ~ " route's distance)"))
p_spar_d

p_spar_sc <- ggplot(spar[Partition == 'SP-threshold'], aes(x = Parameter, y = Prop.served, fill = Approach))
p_spar_sc <- p_spar_sc + geom_boxplot()
p_spar_sc <- p_spar_sc + scale_x_discrete()
p_spar_sc <- p_spar_sc + my_theme_none()
p_spar_sc <- p_spar_sc + scale_fill_manual(values = c("#F0E442", "#D55E00", "#009E73", "#56B4E9"))
p_spar_sc <- p_spar_sc + labs(x = "Threshold t")
p_spar_sc <- p_spar_sc + labs(y = "Prop. Served Customers")
p_spar_sc

#multiplot(p_spar_f_c, p_spar_f_t, p_spar_f_d, p_spar_f_sc, p_spar_c, p_spar_t, p_spar_d, p_spar_sc, cols = 2)
multiplot(p_spar_f_d, p_spar_f_sc, p_spar_d, p_spar_sc, cols = 2)


# EFFECT OF CD-CRSS
# -----------------
cdcrss <- fread("Model.csv")
cdcrss[, Assignment := as.factor(Assignment)]
cdcrss[, Partition := as.factor(Partition)]
cdcrss[, Routing := as.factor(Routing)]
cdcrss[, Zone := as.factor(Zone)]
cdcrss[, Prop.served := Served / Customers]
cdcrss[, Customers := as.factor(Customers)]
cdcrss[, Ratio := as.factor(Ratio)]
cdcrss[, Distribution := as.factor(Distribution)]
cdcrss[, Limit := as.factor(Limit)]
cdcrss[, Parameter := as.factor(Parameter)]
cdcrss[, Classical := as.factor(Classical)]
cdcrss[Classical == 1, Classical := "Current"]
cdcrss[Classical == 0, Classical := "CD-CRSS"]

cdcrss <- cdcrss[Cost != -1]

cdcrss[Assignment == 'SP-Voronoi', Assignment := 'NN']
cdcrss[Assignment == 'LL-EP', Assignment := 'IRNN']
cdcrss[Routing == 'BB', Routing := 'BnB']
cdcrss[, Approach := paste(Assignment, Routing, sep = "-")]
cdcrss$Approach <- factor(cdcrss$Approach, levels = c('NN-NN', 'IRNN-NN', 'NN-BnB', 'IRNN-BnB'))
cdcrss[, Total.service.cost := Dedicated.cost + Service.cost]

cdcrss_prop_f <- function(sd) {
  baseline <- sd[Classical == "Current", -1, with = FALSE]
  other <- sd[Classical == "CD-CRSS", -1, with = FALSE]
  if(nrow(baseline) == 1 & nrow(other) == 1){
    other[1] / baseline[1]
  }
}

sd_cols_cdcrss <- c("Classical", "Cost", "Service.cost", "Total.service.cost")

cdcrss_prop_dt <- cdcrss[, cdcrss_prop_f(.SD), by = list(Seed, Customers, Approach, Stores), .SDcols = sd_cols_cdcrss]

p_cdcrss_prop_c <- ggplot(cdcrss_prop_dt[Approach == "IRNN-BnB"], aes(x = as.factor(Stores), y = Total.service.cost, fill = Approach)) 
p_cdcrss_prop_c <- p_cdcrss_prop_c + geom_boxplot(fill = "#56B4E9") 
p_cdcrss_prop_c <- p_cdcrss_prop_c + scale_x_discrete()
#p_cdcrss_prop_c <- p_cdcrss_prop_c + geom_hline(yintercept=1.0, linetype="twodash", color = "red", size = 1)
p_cdcrss_prop_c <- p_cdcrss_prop_c + geom_hline(yintercept=.65, linetype="twodash", color = "red", size = 1)
p_cdcrss_prop_c <- p_cdcrss_prop_c + my_theme_11()
p_cdcrss_prop_c <- p_cdcrss_prop_c + theme(axis.text = element_text(size = 8, lineheight = 0.9, colour = "black", hjust = 1), axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 10, angle = 90, vjust = 0.5))
p_cdcrss_prop_c <- p_cdcrss_prop_c + labs(x = "Stores")
p_cdcrss_prop_c <- p_cdcrss_prop_c + labs(y = "Prop. of Current Model's Service Cost")
p_cdcrss_prop_c

p_cdcrss_prop_c_2 <- ggplot(cdcrss_prop_dt[Approach == "IRNN-BnB" & Stores >= 5], aes(x = Customers, y = Total.service.cost, fill = Approach)) 
p_cdcrss_prop_c_2 <- p_cdcrss_prop_c_2 + geom_boxplot(fill = "#56B4E9") 
p_cdcrss_prop_c_2 <- p_cdcrss_prop_c_2 + scale_x_discrete()
p_cdcrss_prop_c_2 <- p_cdcrss_prop_c_2 + geom_hline(yintercept=.80, linetype="twodash", color = "red", size = 1)
p_cdcrss_prop_c_2 <- p_cdcrss_prop_c_2 + my_theme_11()
p_cdcrss_prop_c_2 <- p_cdcrss_prop_c_2 + theme(axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 10, angle = 90, vjust = 0.5))
p_cdcrss_prop_c_2 <- p_cdcrss_prop_c_2 + labs(y = "Prop. of Current Model's Service Cost")
p_cdcrss_prop_c_2

summary(cdcrss_prop_dt[Approach == "IRNN-BnB" & Stores >= 5, Total.service.cost])

p_cdcrss_prop_c_3 <- ggplot(cdcrss_prop_dt[Approach == "IRNN-BnB" & Stores >= 5], aes(x = Total.service.cost)) 
p_cdcrss_prop_c_3 <- p_cdcrss_prop_c_3 + geom_histogram(binwidth = .1, alpha = 0.2, col = I("black"))
#p_cdcrss_prop_c_3 <- p_cdcrss_prop_c_3 + scale_x_discrete()
p_cdcrss_prop_c_3 <- p_cdcrss_prop_c_3 + geom_vline(aes(xintercept=mean(Total.service.cost)), linetype="twodash", color = "red", size = 1)
p_cdcrss_prop_c_3 <- p_cdcrss_prop_c_3 + geom_text(aes(label=round(mean(Total.service.cost),2),y=0,x=mean(Total.service.cost)), vjust=-1,col='red',size=5)
p_cdcrss_prop_c_3 <- p_cdcrss_prop_c_3 + my_theme_11()
p_cdcrss_prop_c_3 <- p_cdcrss_prop_c_3 + theme(axis.title.x = element_text(margin = margin(t = 5, r = 0, b = 0, l = 0), size = 10, vjust = 0.5))
p_cdcrss_prop_c_3 <- p_cdcrss_prop_c_3 + labs(x = "Prop. of Current Model's Service Cost")
p_cdcrss_prop_c_3 <- p_cdcrss_prop_c_3 + labs(y = "Frequency")
p_cdcrss_prop_c_3


#hist(cdcrss_prop_dt[Approach == "DIST(ra)-BnB" & Stores >= 5, Total.service.cost])

p_cdcrss_t <- ggplot(cdcrss[Approach == "IRNN-BnB"], aes(x = Customers, y = Elapsed.time, fill = Classical)) 
p_cdcrss_t <- p_cdcrss_t + geom_boxplot() 
p_cdcrss_t <- p_cdcrss_t + scale_x_discrete()
#p_cdcrss_t <- p_cdcrss_t + scale_y_log10()
#p_cdcrss_t <- p_cdcrss_t + geom_hline(yintercept=1.0, linetype="twodash", color = "red", size = 1)
p_cdcrss_t <- p_cdcrss_t + my_theme_01()
p_cdcrss_t <- p_cdcrss_t + scale_fill_manual(values = c("pink", "violet"))
p_cdcrss_t <- p_cdcrss_t + labs(y = "Processing time (s)")
p_cdcrss_t


#multiplot(p_cdcrss_prop_c, p_cdcrss_prop_c_3, p_cdcrss_prop_c_2, p_cdcrss_t, cols = 2)
multiplot(p_cdcrss_prop_c_2, p_cdcrss_t, cols = 2)

summary(cdcrss[Approach == "IRNN-BnB" & Customers == 256, Elapsed.time])



# EFFECT OF TRUE CD
# -----------------
truecd <- fread("TrueCD.csv")
truecd[, Assignment := as.factor(Assignment)]
truecd[, Partition := as.factor(Partition)]
truecd[, Routing := as.factor(Routing)]
truecd[, Zone := as.factor(Zone)]
truecd[, Prop.served := Served / Customers]
truecd[, Customers := as.factor(Customers)]
truecd[, Ratio := as.factor(Ratio)]
truecd[, Distribution := as.factor(Distribution)]
truecd[, Limit := as.factor(Limit)]
truecd[, Parameter := as.factor(Parameter)]
truecd[, Prop.true.cd := as.factor(Prop.true.cd)]

truecd <- truecd[Cost != -1]

truecd[Assignment == 'SP-Voronoi', Assignment := 'NN']
truecd[Assignment == 'LL-EP', Assignment := 'IRNN']
truecd[Routing == 'BB', Routing := 'BnB']
truecd[, Approach := paste(Assignment, Routing, sep = "-")]
truecd$Approach <- factor(truecd$Approach, levels = c('NN-NN', 'IRNN-NN', 'NN-BnB', 'IRNN-BnB'))
truecd[, Total.service.cost := Dedicated.cost + Service.cost]

p_truecd_f_c <- ggplot(truecd[Partition == 'SP-fraction'], aes(x = Prop.true.cd, y = Total.service.cost))
p_truecd_f_c <- p_truecd_f_c + geom_boxplot()
p_truecd_f_c <- p_truecd_f_c + scale_x_discrete()
p_truecd_f_c <- p_truecd_f_c + my_theme_none()
p_truecd_f_c <- p_truecd_f_c + labs(x = "Prop. true CD")
p_truecd_f_c <- p_truecd_f_c + labs(y = "Service Cost (m)")
p_truecd_f_c

p_truecd_c <- ggplot(truecd[Partition != 'SP-fraction'], aes(x = Prop.true.cd, y = Total.service.cost))
p_truecd_c <- p_truecd_c + geom_boxplot()
p_truecd_c <- p_truecd_c + scale_x_discrete()
p_truecd_c <- p_truecd_c + my_theme_none()
p_truecd_c <- p_truecd_c + labs(x = "Prop. true CD")
p_truecd_c <- p_truecd_c + labs(y = "Service Cost (m)")
p_truecd_c



# RETAILER PREFERENCE + MODEL
# ---------------------------
retpref_r <- fread("RetailerPref_Ratio.csv")
retpref_r[, Assignment := as.factor(Assignment)]
retpref_r[, Partition := as.factor(Partition)]
retpref_r[, Routing := as.factor(Routing)]
retpref_r[, Zone := as.factor(Zone)]
retpref_r[, Prop.served := Served / Customers]
retpref_r[, Customers := as.factor(Customers)]
retpref_r[, Ratio := as.factor(Ratio)]
retpref_r[, Distribution := as.factor(Distribution)]
retpref_r[, Limit := as.factor(Limit)]
retpref_r[, Parameter := as.factor(Parameter)]
retpref_r[, Retailer.pref := as.factor(Retailer.pref)]

retpref_r <- retpref_r[Cost != -1]

retpref_r[Assignment == 'SP-Voronoi', Assignment := 'NN']
retpref_r[Assignment == 'LL-EP', Assignment := 'IRNN']
retpref_r[Routing == 'BB', Routing := 'BnB']
retpref_r[, Approach := paste(Assignment, Routing, sep = "-")]
retpref_r$Approach <- factor(retpref_r$Approach, levels = c('NN-NN', 'IRNN-NN', 'NN-BnB', 'IRNN-BnB'))
retpref_r[, Total.service.cost := Dedicated.cost + Service.cost]

retpref_prop_f <- function(sd) {
  baseline <- sd[Classical == TRUE & Retailer.pref == "market_share", -(1:2), with = FALSE]
  other <- sd[Classical == FALSE & Retailer.pref == "neighbour_driver_pref", -(1:2), with = FALSE]
  if(nrow(baseline) == 1 & nrow(other) == 1){
    other[1] / baseline[1]
  }
}

sd_cols_retpref <- c("Classical", "Retailer.pref", "Cost", "Service.cost", "Total.service.cost")

retpref_r_prop_dt <- retpref_r[(Classical == TRUE & Retailer.pref == "market_share") | (Classical == FALSE & Retailer.pref == "neighbour_driver_pref"), retpref_prop_f(.SD), by = list(Seed, Ratio), .SDcols = sd_cols_retpref]

p_retpref_r_prop_c <- ggplot(retpref_r_prop_dt, aes(x = Ratio, y = Total.service.cost, fill = Approach))
p_retpref_r_prop_c <- p_retpref_r_prop_c + geom_boxplot(fill = "#56B4E9")
p_retpref_r_prop_c <- p_retpref_r_prop_c + scale_x_discrete()
#p_retpref_r_prop_c <- p_retpref_r_prop_c + geom_hline(yintercept=.65, linetype="twodash", color = "red", size = 1)
p_retpref_r_prop_c <- p_retpref_r_prop_c + my_theme_none()
p_retpref_r_prop_c <- p_retpref_r_prop_c + theme(axis.text = element_text(size = 8, lineheight = 0.9, colour = "black", hjust = 1), axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 10, angle = 90, vjust = 0.5))
p_retpref_r_prop_c <- p_retpref_r_prop_c + labs(x = "Ratio customers / drivers")
p_retpref_r_prop_c <- p_retpref_r_prop_c + labs(y = "Prop. of Current Model's Service Cost")
p_retpref_r_prop_c


retpref_prop_f_2 <- function(sd) {
  baseline <- sd[Classical == TRUE, -1, with = FALSE]
  other <- sd[Classical == FALSE, -1, with = FALSE]
  if(nrow(baseline) == 1 & nrow(other) == 1){
    other[1] / baseline[1]
  }
}

sd_cols_retpref_2 <- c("Classical", "Cost", "Service.cost", "Total.service.cost")

retpref_r_prop_dt_2 <- retpref_r[Retailer.pref == "market_share", retpref_prop_f_2(.SD), by = list(Seed, Ratio), .SDcols = sd_cols_retpref_2]

retpref_r_prop_dt[, Sharing.economy := TRUE]
retpref_r_prop_dt_2[, Sharing.economy := FALSE]
shec <- rbind(retpref_r_prop_dt, retpref_r_prop_dt_2)

p_shec_prop_c <- ggplot(shec, aes(x = Ratio, y = Total.service.cost, fill = Sharing.economy))
p_shec_prop_c <- p_shec_prop_c + geom_boxplot()
p_shec_prop_c <- p_shec_prop_c + scale_x_discrete()
#p_shec_prop_c <- p_shec_prop_c + geom_hline(yintercept=.65, linetype="twodash", color = "red", size = 1)
p_shec_prop_c <- p_shec_prop_c + my_theme_01()
p_shec_prop_c <- p_shec_prop_c + theme(axis.text = element_text(size = 8, lineheight = 0.9, colour = "black", hjust = 1), axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 10, angle = 90, vjust = 0.5))
p_shec_prop_c <- p_shec_prop_c + labs(x = "Ratio customers / drivers")
p_shec_prop_c <- p_shec_prop_c + labs(y = "Prop. of Current Model's Service Cost")
p_shec_prop_c




retpref_cust <- fread("RetailerPref_Cust.csv")
retpref_cust[, Assignment := as.factor(Assignment)]
retpref_cust[, Partition := as.factor(Partition)]
retpref_cust[, Routing := as.factor(Routing)]
retpref_cust[, Zone := as.factor(Zone)]
retpref_cust[, Prop.served := Served / Customers]
retpref_cust[, Customers := as.factor(Customers)]
retpref_cust[, Ratio := as.factor(Ratio)]
retpref_cust[, Distribution := as.factor(Distribution)]
retpref_cust[, Limit := as.factor(Limit)]
retpref_cust[, Parameter := as.factor(Parameter)]
retpref_cust[, Retailer.pref := as.factor(Retailer.pref)]

retpref_cust <- retpref_cust[Cost != -1]

retpref_cust[Assignment == 'SP-Voronoi', Assignment := 'NN']
retpref_cust[Assignment == 'LL-EP', Assignment := 'IRNN']
retpref_cust[Routing == 'BB', Routing := 'BnB']
retpref_cust[, Approach := paste(Assignment, Routing, sep = "-")]
retpref_cust$Approach <- factor(retpref_cust$Approach, levels = c('NN-NN', 'IRNN-NN', 'NN-BnB', 'IRNN-BnB'))
retpref_cust[, Total.service.cost := Dedicated.cost + Service.cost]

retpref_cust_prop_dt <- retpref_cust[(Classical == TRUE & Retailer.pref == "market_share") | (Classical == FALSE & Retailer.pref == "neighbour_driver_pref"), retpref_prop_f(.SD), by = list(Seed, Customers), .SDcols = sd_cols_retpref]

p_retpref_cust_prop_c <- ggplot(retpref_cust_prop_dt, aes(x = Customers, y = Total.service.cost, fill = Approach))
p_retpref_cust_prop_c <- p_retpref_cust_prop_c + geom_boxplot(fill = "#56B4E9")
p_retpref_cust_prop_c <- p_retpref_cust_prop_c + scale_x_discrete()
p_retpref_cust_prop_c <- p_retpref_cust_prop_c + geom_hline(yintercept=.5, linetype="twodash", color = "red", size = 1)
p_retpref_cust_prop_c <- p_retpref_cust_prop_c + my_theme_none()
p_retpref_cust_prop_c <- p_retpref_cust_prop_c + theme(axis.text = element_text(size = 8, lineheight = 0.9, colour = "black", hjust = 1), axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 10, angle = 90, vjust = 0.5))
p_retpref_cust_prop_c <- p_retpref_cust_prop_c + labs(x = "Customers")
p_retpref_cust_prop_c <- p_retpref_cust_prop_c + labs(y = "Prop. of Current Model's Service Cost")
p_retpref_cust_prop_c


retpref_cust_prop_dt[, Approach := ""]
retpref_cust_prop_dt[, Stores := 0]
retpref_cust_prop_dt[, Approach_2 := "Amazon model"]
cdcrss_prop_dt[, Approach_2 := "Retailer specific"]

shec_2 <- rbind(cdcrss_prop_dt[Approach == "IRNN-BnB" & Stores >= 5], retpref_cust_prop_dt)

p_retpref_cust_prop_c <- ggplot(shec_2, aes(x = Customers, y = Total.service.cost, fill = Approach_2))
p_retpref_cust_prop_c <- p_retpref_cust_prop_c + geom_boxplot()
p_retpref_cust_prop_c <- p_retpref_cust_prop_c + scale_x_discrete()
p_retpref_cust_prop_c <- p_retpref_cust_prop_c + scale_y_continuous(breaks = c(.25, .5, .75, .8, 1., 1.25))
p_retpref_cust_prop_c <- p_retpref_cust_prop_c + geom_hline(yintercept=.8, linetype="twodash", color = "blue", size = 1)
p_retpref_cust_prop_c <- p_retpref_cust_prop_c + geom_hline(yintercept=.5, linetype="twodash", color = "red", size = 1)
p_retpref_cust_prop_c <- p_retpref_cust_prop_c + my_theme_11()
p_retpref_cust_prop_c <- p_retpref_cust_prop_c + theme(axis.text = element_text(size = 8, lineheight = 0.9, colour = "black", hjust = 1), axis.title.y = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0), size = 10, angle = 90, vjust = 0.5))
p_retpref_cust_prop_c <- p_retpref_cust_prop_c + labs(x = "Customers")
p_retpref_cust_prop_c <- p_retpref_cust_prop_c + labs(y = "Prop. of Current Model's Service Cost")
p_retpref_cust_prop_c

