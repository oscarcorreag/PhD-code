setwd("C:/Users/oscarcg/Documents/phd/code/Experiments/files/")

users <- read.csv("50 samples/users.csv", header = FALSE)
names(users) <- c("alg", "seed", "n_size", "hs_size", "u", "p", "cap", "samp", "e_time", "cost", "gr", "avg_dr", "num_cars", "avg_or")

pois <- read.csv("50 samples/POIs.csv", header = FALSE)
names(pois) <- c("alg", "seed", "n_size", "hs_size", "u", "p", "cap", "samp", "e_time", "cost", "gr", "avg_dr", "num_cars", "avg_or")

hotspots <- read.csv("50 samples/hotspots.csv", header = FALSE)
names(hotspots) <- c("alg", "seed", "n_size", "hs_size", "u", "p", "cap", "samp", "e_time", "cost", "gr", "avg_dr", "num_cars", "avg_or")
hotspots$prop <- 0
hotspots[with(hotspots, hs_size < 450), "prop"] <- 0.03
hotspots[with(hotspots, hs_size > 450 & hs_size < 900), "prop"] <- 0.06
hotspots[with(hotspots, hs_size > 900 & hs_size < 1850), "prop"] <- 0.12
#hotspots[with(hotspots, hs_size > 1300 & hs_size < 1750), "prop"] <- 0.5
hotspots[with(hotspots, hs_size > 1850), "prop"] <- 0.25

cap <- read.csv("50 samples/capacity.csv", header = FALSE)
names(cap) <- c("alg", "seed", "n_size", "hs_size", "u", "p", "cap", "samp", "e_time", "cost", "gr", "avg_dr", "num_cars", "avg_or")

n_size <- read.csv("50 samples/network.csv", header = FALSE)
names(n_size) <- c("alg", "seed", "n_size", "hs_size", "u", "p", "cap", "samp", "e_time", "cost", "gr", "avg_dr", "num_cars", "avg_or")


library(ggplot2)

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
      legend.justification = c(0, 0),
      legend.position      = c(0, 0),
      #legend.title         = element_blank(),
      
      #legend.text           = element_text(size = 8, lineheight = 0.9, hjust = 1),
      #legend.title          = element_text(size = 9),
      
      # dark strips with light text (inverse contrast compared to theme_grey)
      strip.background = element_rect(fill = "grey70", colour = NA),
      strip.text       = element_text(colour = "white", size = rel(0.8)),
      
      #axis.title.x = axis_x_title,
      #axis.title.y = axis_y_title,
      axis.title.x = element_text(size = 9, vjust = 0.5),
      axis.title.y = element_text(size = 9, angle = 90, vjust = 0.5),
      #axis.text    = element_text(size = 8, lineheight = 0.9, colour = "grey50", hjust = 1),
      axis.text    = element_text(size = 8, lineheight = 0.9, colour = "black", hjust = 1),
      
      complete = TRUE
    )
  
}

# Multiple plot function
#
# ggplot objects can be passed in ..., or to plotlist (as a list of ggplot objects)
# - cols:   Number of columns in layout
# - layout: A matrix specifying the layout. If present, 'cols' is ignored.
#
# If the layout is something like matrix(c(1,2,3,3), nrow=2, byrow=TRUE),
# then plot 1 will go in the upper left, 2 will go in the upper right, and
# 3 will go all the way across the bottom.
#
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

library(scales)

#COST
p_u_c <- ggplot(users, aes(x=u, y=cost, colour=alg, linetype=alg))
#p_u_c <- p_u_c + geom_point(alpha=.3, size=2)
p_u_c <- p_u_c + geom_smooth(alpha=.2, size=1)
p_u_c <- p_u_c + scale_x_log10(breaks = c(2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048), labels=math_format(2^.x)(1:11))
p_u_c <- p_u_c + my_theme()
p_u_c <- p_u_c + labs(x="# Users", y="Cost")
p_u_c

p_p_c <- ggplot(pois, aes(x=p, y=cost, colour=alg, linetype=alg))
#p_p_c <- p_p_c + geom_point(alpha=.3, size=2)
p_p_c <- p_p_c + geom_smooth(alpha=.2, size=1)
p_p_c <- p_p_c + scale_x_log10(breaks = c(10, 20, 40, 80, 160, 320, 640))
p_p_c <- p_p_c + my_theme()
p_p_c <- p_p_c + labs(x="# POIs", y="Cost")

p_h_c <- ggplot(hotspots, aes(x=prop, y=cost, colour=alg, linetype=alg))
#p_h_c <- p_h_c + geom_point(alpha=.3, size=2)
p_h_c <- p_h_c + geom_smooth(alpha=.2, size=1)
p_h_c <- p_h_c + scale_x_continuous(breaks = c(0.03, 0.07, 0.11, 0.15, 0.2), labels=c("3%", "7%", "11%", "15%", "20%"))
p_h_c <- p_h_c + my_theme()
p_h_c <- p_h_c + labs(x="% Hot-spots", y="Cost")

p_ca_c <- ggplot(cap, aes(x=cap, y=cost, colour=alg, linetype=alg))
#p_ca_c <- p_ca_c + geom_point(alpha=.3, size=2)
p_ca_c <- p_ca_c + geom_smooth(alpha=.2, size=1)
p_ca_c <- p_ca_c + scale_x_continuous(breaks = c(4, 5, 6, 7, 8, 9, 10))
p_ca_c <- p_ca_c + my_theme()
p_ca_c <- p_ca_c + labs(x="Car capacity", y="Cost")

p_n_c <- ggplot(n_size, aes(x=n_size, y=cost, colour=alg, linetype=alg))
#p_n_c <- p_n_c + geom_point(alpha=.3, size=2)
p_n_c <- p_n_c + geom_smooth(alpha=.2, size=1)
p_n_c <- p_n_c + scale_x_log10(breaks = c(1250, 2500, 5000, 10000, 20000, 40000, 80000), labels=c("1.25k", "2.5k", "5k", "10k", "20k", "40k", "80k"))
p_n_c <- p_n_c + my_theme()
p_n_c <- p_n_c + labs(x="# Vertices", y="Cost")

#GAIN RATIO
p_u_g <- ggplot(users, aes(x=u, y=gr, colour=alg, linetype=alg))
p_u_g <- p_u_g + geom_point(alpha=.3, size=2)
p_u_g <- p_u_g + geom_smooth(alpha=.2, size=1)
p_u_g <- p_u_g + scale_x_log10(breaks = c(2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048), labels=math_format(2^.x)(1:11))
p_u_g <- p_u_g + my_theme() 
p_u_g <- p_u_g + labs(x="# Users", y="Gain ratio")

p_p_g <- ggplot(pois, aes(x=p, y=gr, colour=alg, linetype=alg))
p_p_g <- p_p_g + geom_point(alpha=.3, size=2)
p_p_g <- p_p_g + geom_smooth(alpha=.2, size=1)
p_p_g <- p_p_g + scale_x_log10(breaks = c(10, 20, 40, 80, 160, 320, 640))
p_p_g <- p_p_g + my_theme()
p_p_g <- p_p_g + labs(x="# POIs", y="Gain ratio")

p_h_g <- ggplot(hotspots, aes(x=prop, y=gr, colour=alg, linetype=alg))
p_h_g <- p_h_g + geom_point(alpha=.3, size=2)
p_h_g <- p_h_g + geom_smooth(alpha=.2, size=1)
p_h_g <- p_h_g + scale_x_continuous(breaks = c(0.03, 0.06, 0.12, 0.25), labels=c("3%", "6%", "12%", "25%"))
p_h_g <- p_h_g + my_theme()
p_h_g <- p_h_g + labs(x="% Hot-spots", y="Gain ratio")

p_ca_g <- ggplot(cap, aes(x=cap, y=gr, colour=alg, linetype=alg))
p_ca_g <- p_ca_g + geom_point(alpha=.3, size=2)
p_ca_g <- p_ca_g + geom_smooth(alpha=.2, size=1)
p_ca_g <- p_ca_g + scale_x_continuous(breaks = c(4, 5, 6, 7, 8, 9, 10))
p_ca_g <- p_ca_g + my_theme()
p_ca_g <- p_ca_g + labs(x="Car capacity", y="Gain ratio")

p_n_g <- ggplot(n_size, aes(x=n_size, y=gr, colour=alg, linetype=alg))
p_n_g <- p_n_g + geom_point(alpha=.3, size=2)
p_n_g <- p_n_g + geom_smooth(alpha=.2, size=1)
p_n_g <- p_n_g + scale_x_log10(breaks = c(1250, 2500, 5000, 10000, 20000, 40000, 80000), labels=c("1.25k", "2.5k", "5k", "10k", "20k", "40k", "80k"))
p_n_g <- p_n_g + my_theme()
p_n_g <- p_n_g + labs(x="# Vertices", y="Gain ratio")

multiplot(p_u_c, p_p_c, p_h_c, p_ca_c, p_n_c, p_u_g, p_p_g, p_h_g, p_ca_g, p_n_g, cols=2)


#TIME
p_u_t <- ggplot(users, aes(x=u, y=e_time, colour=alg, linetype=alg))
#p_u_t <- p_u_t + geom_point(alpha=.3, size=2)
p_u_t <- p_u_t + geom_smooth(alpha=.2, size=1)
p_u_t <- p_u_t + scale_x_log10(breaks = c(2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048), labels=math_format(2^.x)(1:11))
p_u_t <- p_u_t + my_theme()
p_u_t <- p_u_t + labs(x="# Users", y="Processing time (s)")
p_u_t

p_p_t <- ggplot(pois, aes(x=p, y=e_time, colour=alg, linetype=alg))
#p_p_t <- p_p_t + geom_point(alpha=.3, size=2)
p_p_t <- p_p_t + geom_smooth(alpha=.2, size=1)
p_p_t <- p_p_t + scale_x_log10(breaks = c(10, 20, 40, 80, 160, 320, 640))
p_p_t <- p_p_t + my_theme()
p_p_t <- p_p_t + labs(x="# POIs", y="Processing time (s)")
p_p_t

p_h_t <- ggplot(hotspots, aes(x=prop, y=e_time, colour=alg, linetype=alg))
#p_h_t <- p_h_t + geom_point(alpha=.3, size=2)
p_h_t <- p_h_t + geom_smooth(alpha=.2, size=1)
p_h_t <- p_h_t + scale_x_continuous(breaks = c(0.03, 0.06, 0.12, 0.25), labels=c("3%", "6%", "12%", "25%"))
p_h_t <- p_h_t + my_theme()
p_h_t <- p_h_t + labs(x="% Hot-spots", y="Processing time (s)")
p_h_t

p_ca_t <- ggplot(cap, aes(x=cap, y=e_time, colour=alg, linetype=alg))
#p_ca_t <- p_ca_t + geom_point(alpha=.3, size=2)
p_ca_t <- p_ca_t + geom_smooth(alpha=.2, size=1)
p_ca_t <- p_ca_t + scale_x_continuous(breaks = c(4, 5, 6, 7, 8, 9, 10))
p_ca_t <- p_ca_t + my_theme()
p_ca_t <- p_ca_t + labs(x="Car capacity", y="Processing time (s)")
p_ca_t

p_n_t <- ggplot(n_size, aes(x=n_size, y=e_time, colour=alg, linetype=alg))
#p_n_t <- p_n_t + geom_point(alpha=.3, size=2)
p_n_t <- p_n_t + geom_smooth(alpha=.2, size=1)
p_n_t <- p_n_t + scale_x_log10(breaks = c(1250, 2500, 5000, 10000, 20000, 40000, 80000), labels=c("1.25k", "2.5k", "5k", "10k", "20k", "40k", "80k"))
p_n_t <- p_n_t + my_theme()
p_n_t <- p_n_t + labs(x="# Vertices", y="Processing time (s)")
p_n_t

#AVG. DETOUR RATIO
p_u_d <- ggplot(users, aes(x=u, y=avg_dr, colour=alg, linetype=alg))
p_u_d <- p_u_d + geom_point(alpha=.3, size=2)
p_u_d <- p_u_d + geom_smooth(alpha=.2, size=1)
p_u_d <- p_u_d + scale_x_log10(breaks = c(2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048), labels=math_format(2^.x)(1:11))
p_u_d <- p_u_d + my_theme() 
p_u_d <- p_u_d + labs(x="# Users", y="Avg. detour ratio")

p_p_d <- ggplot(pois, aes(x=p, y=avg_dr, colour=alg, linetype=alg))
p_p_d <- p_p_d + geom_point(alpha=.3, size=2)
p_p_d <- p_p_d + geom_smooth(alpha=.2, size=1)
p_p_d <- p_p_d + scale_x_log10(breaks = c(10, 20, 40, 80, 160, 320, 640))
p_p_d <- p_p_d + my_theme()
p_p_d <- p_p_d + labs(x="# POIs", y="Avg. detour ratio")

p_h_d <- ggplot(hotspots, aes(x=prop, y=avg_dr, colour=alg, linetype=alg))
p_h_d <- p_h_d + geom_point(alpha=.3, size=2)
p_h_d <- p_h_d + geom_smooth(alpha=.2, size=1)
p_h_d <- p_h_d + scale_x_continuous(breaks = c(0.03, 0.07, 0.11, 0.15, 0.2), labels=c("3%", "7%", "11%", "15%", "20%"))
p_h_d <- p_h_d + my_theme()
p_h_d <- p_h_d + labs(x="% Hot-spots", y="Avg. detour ratio")

p_ca_d <- ggplot(cap, aes(x=cap, y=avg_dr, colour=alg, linetype=alg))
p_ca_d <- p_ca_d + geom_point(alpha=.3, size=2)
p_ca_d <- p_ca_d + geom_smooth(alpha=.2, size=1)
p_ca_d <- p_ca_d + scale_x_continuous(breaks = c(4, 5, 6, 7, 8, 9, 10))
p_ca_d <- p_ca_d + my_theme()
p_ca_d <- p_ca_d + labs(x="Car capacity", y="Avg. detour ratio")

p_n_d <- ggplot(n_size, aes(x=n_size, y=avg_dr, colour=alg, linetype=alg))
p_n_d <- p_n_d + geom_point(alpha=.3, size=2)
p_n_d <- p_n_d + geom_smooth(alpha=.2, size=1)
p_n_d <- p_n_d + scale_x_log10(breaks = c(1250, 2500, 5000, 10000, 20000, 40000, 80000), labels=c("1.25k", "2.5k", "5k", "10k", "20k", "40k", "80k"))
p_n_d <- p_n_d + my_theme()
p_n_d <- p_n_d + labs(x="# Vertices", y="Avg. detour ratio")

multiplot(p_u_t, p_p_t, p_h_t, p_ca_t, p_n_t, p_u_d, p_p_d, p_h_d, p_ca_d, p_n_d, cols=2)


#NUM. CARS
p_u_nc <- ggplot(users, aes(x=u, y=num_cars, colour=alg, linetype=alg))
p_u_nc <- p_u_nc + geom_point(alpha=.3, size=2)
p_u_nc <- p_u_nc + geom_smooth(alpha=.2, size=1)
p_u_nc <- p_u_nc + scale_x_log10(breaks = c(2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048), labels=math_format(2^.x)(1:11))
p_u_nc <- p_u_nc + my_theme()
p_u_nc <- p_u_nc + labs(x="# Users", y="# Cars")

p_p_nc <- ggplot(pois, aes(x=p, y=num_cars, colour=alg, linetype=alg))
p_p_nc <- p_p_nc + geom_point(alpha=.3, size=2)
p_p_nc <- p_p_nc + geom_smooth(alpha=.2, size=1)
p_p_nc <- p_p_nc + scale_x_log10(breaks = c(10, 20, 40, 80, 160, 320, 640))
p_p_nc <- p_p_nc + my_theme()
p_p_nc <- p_p_nc + labs(x="# POIs", y="# Cars")

p_h_nc <- ggplot(hotspots, aes(x=prop, y=num_cars, colour=alg, linetype=alg))
p_h_nc <- p_h_nc + geom_point(alpha=.3, size=2)
p_h_nc <- p_h_nc + geom_smooth(alpha=.2, size=1)
p_h_nc <- p_h_nc + scale_x_continuous(breaks = c(0.03, 0.07, 0.11, 0.15, 0.2), labels=c("3%", "7%", "11%", "15%", "20%"))
p_h_nc <- p_h_nc + my_theme()
p_h_nc <- p_h_nc + labs(x="% Hot-spots", y="# Cars")

p_ca_nc <- ggplot(cap, aes(x=cap, y=num_cars, colour=alg, linetype=alg))
p_ca_nc <- p_ca_nc + geom_point(alpha=.3, size=2)
p_ca_nc <- p_ca_nc + geom_smooth(alpha=.2, size=1)
p_ca_nc <- p_ca_nc + scale_x_continuous(breaks = c(4, 5, 6, 7, 8, 9, 10))
p_ca_nc <- p_ca_nc + my_theme()
p_ca_nc <- p_ca_nc + labs(x="Car capacity", y="# Cars")

p_n_nc <- ggplot(n_size, aes(x=n_size, y=num_cars, colour=alg, linetype=alg))
p_n_nc <- p_n_nc + geom_point(alpha=.3, size=2)
p_n_nc <- p_n_nc + geom_smooth(alpha=.2, size=1)
p_n_nc <- p_n_nc + scale_x_log10(breaks = c(1250, 2500, 5000, 10000, 20000, 40000, 80000), labels=c("1.25k", "2.5k", "5k", "10k", "20k", "40k", "80k"))
p_n_nc <- p_n_nc + my_theme()
p_n_nc <- p_n_nc + labs(x="# Vertices", y="# Cars")

#AVG. OCCUPANCY RATIO
p_u_o <- ggplot(users, aes(x=u, y=avg_or, colour=alg, linetype=alg))
p_u_o <- p_u_o + geom_point(alpha=.3, size=2)
p_u_o <- p_u_o + geom_smooth(alpha=.2, size=1)
p_u_o <- p_u_o + scale_x_log10(breaks = c(2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048), labels=math_format(2^.x)(1:11))
p_u_o <- p_u_o + my_theme() 
p_u_o <- p_u_o + labs(x="# Users", y="Avg. occupancy ratio")

p_p_o <- ggplot(pois, aes(x=p, y=avg_or, colour=alg, linetype=alg))
p_p_o <- p_p_o + geom_point(alpha=.3, size=2)
p_p_o <- p_p_o + geom_smooth(alpha=.2, size=1)
p_p_o <- p_p_o + scale_x_log10(breaks = c(10, 20, 40, 80, 160, 320, 640))
p_p_o <- p_p_o + my_theme()
p_p_o <- p_p_o + labs(x="# POIs", y="Avg. occupancy ratio")

p_h_o <- ggplot(hotspots, aes(x=prop, y=avg_or, colour=alg, linetype=alg))
p_h_o <- p_h_o + geom_point(alpha=.3, size=2)
p_h_o <- p_h_o + geom_smooth(alpha=.2, size=1)
p_h_o <- p_h_o + scale_x_continuous(breaks = c(0.03, 0.07, 0.11, 0.15, 0.2), labels=c("3%", "7%", "11%", "15%", "20%"))
p_h_o <- p_h_o + my_theme()
p_h_o <- p_h_o + labs(x="% Hot-spots", y="Avg. occupancy ratio")

p_ca_o <- ggplot(cap, aes(x=cap, y=avg_or, colour=alg, linetype=alg))
p_ca_o <- p_ca_o + geom_point(alpha=.3, size=2)
p_ca_o <- p_ca_o + geom_smooth(alpha=.2, size=1)
p_ca_o <- p_ca_o + scale_x_continuous(breaks = c(4, 5, 6, 7, 8, 9, 10))
p_ca_o <- p_ca_o + my_theme()
p_ca_o <- p_ca_o + labs(x="Car capacity", y="Avg. occupancy ratio")

p_n_o <- ggplot(n_size, aes(x=n_size, y=avg_or, colour=alg, linetype=alg))
p_n_o <- p_n_o + geom_point(alpha=.3, size=2)
p_n_o <- p_n_o + geom_smooth(alpha=.2, size=1)
p_n_o <- p_n_o + scale_x_log10(breaks = c(1250, 2500, 5000, 10000, 20000, 40000, 80000), labels=c("1.25k", "2.5k", "5k", "10k", "20k", "40k", "80k"))
p_n_o <- p_n_o + my_theme()
p_n_o <- p_n_o + labs(x="# Vertices", y="Avg. occupancy ratio")

multiplot(p_u_nc, p_p_nc, p_h_nc, p_ca_nc, p_n_nc, p_u_o, p_p_o, p_h_o, p_ca_o, p_n_o, cols=2)