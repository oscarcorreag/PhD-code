setwd("C:/Users/oscarcg/Dropbox/Education/Unimelb PhD/code/Experiments/files/Ride-sharing_is_About_Agreeing_on_a_Destination_TSAS_2018/")

# Retrieve data.
exp1 <- read.csv("25Apr2018_231144.csv", header = TRUE)
exp2 <- read.csv("26Apr2018_083909.csv", header = TRUE)
exp3 <- read.csv("29Apr2018_163325.csv", header = TRUE)
exp4 <- read.csv("29Apr2018_173624.csv", header = TRUE)
exp5 <- read.csv("30Apr2018_102000.csv", header = TRUE)
exp6 <- read.csv("01May2018_031047.csv", header = TRUE)
exp7 <- read.csv("01May2018_224700.csv", header = TRUE)
exp8 <- read.csv("05May2018_005504.csv", header = TRUE)

# Create a master dataframe.
exp <- rbind(exp1, exp2, exp3, exp4, exp5, exp6, exp7, exp8)
#exp <- rbind(exp8)

# Convert data frame to data table to filtering and grouping.
library(data.table)

exp_dt <- as.data.table(exp)

# Group by individual samples and aggregate dependent variables.
# Normalise the dependent variables by considering VST-NCA values as basis.
normalize <- function(sd) {
  ca <- sd[Algorithm == "VST-CA", -1, with = FALSE]
  nca <- sd[Algorithm == "VST-NCA", -1, with = FALSE]
  if(nrow(ca) == 1 & nrow(nca) == 1){
    ca[1] / nca[1]
  }
}

by_cols <- c("Net.size", "Min.cap", "Max.cap", "Merge.cells", "Num.queries", "Num.users", "Prop.POIs", "Num.POIs", "POIs.dist", "Alpha", "Beta", "Sample")
sd_cols <- c("Algorithm", "Cost", "WARL", "MRL", "Elapsed.time")

pure <- exp_dt[Strategy == "N/A" | Strategy == "pure", normalize(.SD), by = by_cols, .SDcols = sd_cols]
pure$Strategy <- "Pure"

mixed <- exp_dt[Strategy == "N/A" | Strategy == "mixed", normalize(.SD), by = by_cols, .SDcols = sd_cols]
mixed$Strategy <- "Mixed"

# Merged strategies
exp_dt_2 <- rbind(pure, mixed)
#exp_dt_2 <- rbind(mixed)

# Create new columns.
exp_dt_2$Total.users <- exp_dt_2$Num.queries * exp_dt_2$Num.users
exp_dt_2$Total.POIs <- exp_dt_2$Num.queries * exp_dt_2$Num.POIs
exp_dt_2$Ratio.total.users.net <- exp_dt_2$Total.users / exp_dt_2$Net.size
exp_dt_2$Ratio.total.POIs.net <- exp_dt_2$Total.POIs / exp_dt_2$Net.size
exp_dt_2$Ratio.POIs.users <- exp_dt_2$Num.POIs / exp_dt_2$Num.users
exp_dt_2$Ratio.users.queries <- exp_dt_2$Num.users / exp_dt_2$Num.queries

# Some plots.
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
      legend.justification = c(1, 1),
      legend.position      = c(1, 1),
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

# [POIs.dist, Strategy, Ratio.total.users.net] V Cost
p1 <- ggplot(exp_dt_2, aes(x=Ratio.total.users.net, y=Cost, color=POIs.dist, linetype=Strategy))
p1 <- p1 + geom_smooth(alpha=.2, size=1, se=FALSE, span=0.8)
p1 <- p1 + scale_x_continuous(minor_breaks = c())
p1 <- p1 + geom_hline(yintercept=1.0, linetype="twodash", color = "black")
p1 <- p1 + my_theme()
p1

# [POIs.dist, Strategy, Ratio.total.users.net] V WARL
p2 <- ggplot(exp_dt_2, aes(x=Ratio.total.users.net, y=WARL, color=POIs.dist, linetype=Strategy))
p2 <- p2 + geom_smooth(alpha=.2, size=1, se=FALSE, span=0.8)
p2 <- p2 + scale_x_continuous(minor_breaks = c())
p2 <- p2 + geom_hline(yintercept=1.0, linetype="twodash", color = "black")
p2 <- p2 + my_theme()
p2

# [POIs.dist, Strategy, Ratio.total.users.net] V MRL
p3 <- ggplot(exp_dt_2, aes(x=Ratio.total.users.net, y=MRL, color=POIs.dist, linetype=Strategy))
p3 <- p3 + geom_smooth(alpha=.2, size=1, se=FALSE, span=0.8)
p3 <- p3 + scale_x_continuous(minor_breaks = c())
p3 <- p3 + geom_hline(yintercept=1.0, linetype="twodash", color = "black")
p3 <- p3 + my_theme()
p3

# [POIs.dist, Strategy, Ratio.users.queries] V Cost
#p4 <- ggplot(exp_dt_2[Ratio.users.queries <= 2], aes(x=Ratio.users.queries, y=Cost, color=POIs.dist, linetype=Strategy))
p4 <- ggplot(exp_dt_2, aes(x=Ratio.users.queries, y=Cost, color=POIs.dist, linetype=Strategy))
p4 <- p4 + geom_smooth(alpha=.2, size=1, se=FALSE, span=0.8)
p4 <- p4 + scale_x_continuous(minor_breaks = c())
p4 <- p4 + geom_hline(yintercept=1.0, linetype="twodash", color = "black")
p4 <- p4 + my_theme()
p4

# [POIs.dist, Strategy, Ratio.users.queries] V WARL
#p5 <- ggplot(exp_dt_2[Ratio.users.queries <= 2], aes(x=Ratio.users.queries, y=WARL, color=POIs.dist, linetype=Strategy))
p5 <- ggplot(exp_dt_2, aes(x=Ratio.users.queries, y=WARL, color=POIs.dist, linetype=Strategy))
p5 <- p5 + geom_smooth(alpha=.2, size=1, se=FALSE, span=0.8)
p5 <- p5 + scale_x_continuous(minor_breaks = c())
p5 <- p5 + geom_hline(yintercept=1.0, linetype="twodash", color = "black")
p5 <- p5 + my_theme()
p5

# [POIs.dist, Strategy, Ratio.users.queries] V MRL
#p6 <- ggplot(exp_dt_2[Ratio.users.queries <= 2], aes(x=Ratio.users.queries, y=MRL, color=POIs.dist, linetype=Strategy))
p6 <- ggplot(exp_dt_2, aes(x=Ratio.users.queries, y=MRL, color=POIs.dist, linetype=Strategy))
p6 <- p6 + geom_smooth(alpha=.2, size=1, se=FALSE, span=0.8)
p6 <- p6 + scale_x_continuous(minor_breaks = c())
p6 <- p6 + geom_hline(yintercept=1.0, linetype="twodash", color = "black")
p6 <- p6 + my_theme()
p6


#p9 <- ggplot(exp_dt_2[Ratio.total.POIs.net <= 0.15], aes(x=Ratio.total.POIs.net, y=MRL, color=POIs.dist, linetype=Strategy))
p9 <- ggplot(exp_dt_2, aes(x=Ratio.total.POIs.net, y=MRL, color=POIs.dist, linetype=Strategy))
p9 <- p9 + geom_smooth(alpha=.2, size=1, se=FALSE, span=0.5)
p9 <- p9 + scale_x_continuous(minor_breaks = c())
p9 <- p9 + geom_hline(yintercept=1.0, linetype="twodash", color = "black")
p9 <- p9 + my_theme()
p9

p12 <- ggplot(exp_dt_2, aes(x=Alpha, y=MRL, color=POIs.dist, linetype=Strategy))
p12 <- p12 + geom_boxplot()
p12 <- p12 + scale_x_discrete()
#p12 <- p12 + scale_x_continuous(minor_breaks = c())
p12 <- p12 + geom_hline(yintercept=1.0, linetype="twodash", color = "black")
p12 <- p12 + my_theme()
p12


# What is the extent of congestion given by ratio Users/[Net Size] with different:
# (a) Distribution of POIs
# (b) Proportion of POIs
