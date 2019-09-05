library(data.table)
library(ggplot2)

setwd("C:/Users/oscarcg/Documents/phd/code/Pickup-Delivery/test/files/")

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

# ----
# Parameter: number of customers

exp_nc <- fread("csdp_ap_30Aug2019_013156_num_customers.csv")
exp_nc$Approach <- as.factor(exp_nc$Approach)
exp_nc$Parameter <- as.factor(exp_nc$Parameter)
exp_nc$Seed <- as.factor(exp_nc$Seed)
exp_nc$Zone <- as.factor(exp_nc$Zone)
exp_nc$Distribution <- as.factor(exp_nc$Distribution)

exp_nc[, Ad.hoc.cost.prop := Ad.hoc.cost/Cost]
exp_nc[, Ded.cost.prop := 1 - Ad.hoc.cost.prop]
exp_nc[, Cust.density := Customers/Net.size]
exp_nc[, Stores.density := Stores/Net.size]
exp_nc[, Ad.hoc.serv.cost := Ad.hoc.cost - Ad.hoc.cost/Avg.detour]
exp_nc[, Service.cost.1 := Ad.hoc.serv.cost + Dedicated.cost]
exp_nc[, Ad.hoc.serv.cost.prop := Ad.hoc.serv.cost/Service.cost.1]
exp_nc[, Ded.serv.cost.prop := 1 - Ad.hoc.serv.cost.prop]
exp_nc[, Service.cost.2 := Ad.hoc.serv.cost + 2 * Dedicated.cost]
exp_nc[, Service.cost.3 := Ad.hoc.serv.cost + 3 * Dedicated.cost]
exp_nc[Ad.hoc.serv.cost < 0.1, Ad.hoc.serv.cost := 0]
exp_nc[Approach == "SP-Voronoi-DT", Appr := "Voronoi"]
exp_nc[Approach == "SP-fraction-DT", Appr := paste("Fr: ", Parameter)]
exp_nc[Approach == "SP-threshold-DT", Appr := paste("Thr: ", Parameter)]

p1_nc <- ggplot(exp_nc, aes(x = as.factor(Customers) , y = Service.cost.1, fill = Appr))
p1_nc <- p1_nc + geom_boxplot()
p1_nc <- p1_nc + scale_x_discrete()
#p1_nc <- p1_nc + scale_y_log10()
#p1_nc <- p1_nc + my_theme()
p1_nc <- p1_nc + labs(x = "Number of customers")
p1_nc <- p1_nc + labs(y = "Service cost")
p1_nc

p2_nc <- ggplot(exp_nc, aes(x = as.factor(Customers) , y = Elapsed.time, fill = Appr))
p2_nc <- p2_nc + geom_boxplot()
p2_nc <- p2_nc + scale_x_discrete()
p2_nc <- p2_nc + scale_y_log10()
#p2_nc <- p2_nc + my_theme()
p2_nc <- p2_nc + labs(x = "Number of customers")
p2_nc <- p2_nc + labs(y = "Processing time (s)")
p2_nc

p3_nc <- ggplot(exp_nc[Avg.detour < 4], aes(x = as.factor(Customers) , y = Avg.detour, fill = Appr))
p3_nc <- p3_nc + geom_boxplot()
p3_nc <- p3_nc + scale_x_discrete()
#p3_nc <- p3_nc + my_theme()
p3_nc <- p3_nc + labs(x = "Number of customers")
p3_nc <- p3_nc + labs(y = "Avg. Detour")
p3_nc

p4_nc <- ggplot(exp_nc, aes(x = as.factor(Customers) , y = Ded.serv.cost.prop, fill = Appr))
p4_nc <- p4_nc + geom_boxplot()
p4_nc <- p4_nc + scale_x_discrete()
#p4_nc <- p4_nc + my_theme()
p4_nc <- p4_nc + labs(x = "Number of customers")
p4_nc <- p4_nc + labs(y = "Prop. Service Cost (Dedicated)")
p4_nc

#p5 <- ggplot(exp_nc[Customers == 256], aes(x = Stores.density, y = Cost))
#p5 <- p5 + geom_point() + facet_wrap(~ Appr, nrow = 2)
#p5 <- p5 + my_theme()
#p5 <- p5 + labs(x = "Customer density")
#p5



# ----
# Parameter: ratio customer to drivers

exp_ra <- fread("csdp_ap_01Sep2019_051726_ratio.csv")
exp_ra$Approach <- as.factor(exp_ra$Approach)
exp_ra$Parameter <- as.factor(exp_ra$Parameter)
exp_ra$Seed <- as.factor(exp_ra$Seed)
exp_ra$Zone <- as.factor(exp_ra$Zone)
exp_ra$Distribution <- as.factor(exp_ra$Distribution)

exp_ra[, Ad.hoc.cost.prop := Ad.hoc.cost/Cost]
exp_ra[, Ded.cost.prop := 1 - Ad.hoc.cost.prop]
exp_ra[, Cust.density := Customers/Net.size]
exp_ra[, Stores.density := Stores/Net.size]
exp_ra[, Ad.hoc.serv.cost := Ad.hoc.cost - Ad.hoc.cost/Avg.detour]
exp_ra[, Service.cost.1 := Ad.hoc.serv.cost + Dedicated.cost]
exp_ra[, Ad.hoc.serv.cost.prop := Ad.hoc.serv.cost/Service.cost.1]
exp_ra[, Ded.serv.cost.prop := 1 - Ad.hoc.serv.cost.prop]
exp_ra[, Service.cost.2 := Ad.hoc.serv.cost + 2 * Dedicated.cost]
exp_ra[, Service.cost.3 := Ad.hoc.serv.cost + 3 * Dedicated.cost]
exp_ra[Ad.hoc.serv.cost < 0.1, Ad.hoc.serv.cost := 0]
exp_ra[Approach == "SP-Voronoi-DT", Appr := "Voronoi"]
exp_ra[Approach == "SP-fraction-DT", Appr := paste("Fr: ", Parameter)]
exp_ra[Approach == "SP-threshold-DT", Appr := paste("Thr: ", Parameter)]

p1_ra <- ggplot(exp_ra, aes(x = as.factor(Ratio) , y = Service.cost.1, fill = Appr))
p1_ra <- p1_ra + geom_boxplot()
p1_ra <- p1_ra + scale_x_discrete()
#p1 <- p1 + scale_y_log10()
#p1 <- p1 + my_theme()
p1_ra <- p1_ra + labs(x = "Ratio (Customers/Drivers)")
p1_ra <- p1_ra + labs(y = "Service cost")
p1_ra

p2_ra <- ggplot(exp_ra, aes(x = as.factor(Ratio), y = Elapsed.time, fill = Appr))
p2_ra <- p2_ra + geom_boxplot()
p2_ra <- p2_ra + scale_x_discrete()
#p2_ra <- p2_ra + scale_y_log10()
#p2_ra <- p2_ra + my_theme()
p2_ra <- p2_ra + labs(x = "Ratio (Customers/Drivers)")
p2_ra <- p2_ra + labs(y = "Processing time (s)")
p2_ra

p3_ra <- ggplot(exp_ra, aes(x = as.factor(Ratio), y = Avg.detour, fill = Appr))
p3_ra <- p3_ra + geom_boxplot()
p3_ra <- p3_ra + scale_x_discrete()
#p3_ra <- p3_ra + my_theme()
p3_ra <- p3_ra + labs(x = "Ratio (Customers/Drivers)")
p3_ra <- p3_ra + labs(y = "Avg. Detour")
p3_ra

p4_ra <- ggplot(exp_ra, aes(x = as.factor(Ratio), y = Ded.serv.cost.prop, fill = Appr))
p4_ra <- p4_ra + geom_boxplot()
p4_ra <- p4_ra + scale_x_discrete()
#p4_ra <- p4_ra + my_theme()
p4_ra <- p4_ra + labs(x = "Ratio (Customers/Drivers)")
p4_ra <- p4_ra + labs(y = "Prop. Service Cost (Dedicated)")
p4_ra


#p5 <- ggplot(exp_ra, aes(x = Ded.cost.prop, y = Cost, color=Appr))
#p5 <- p5 + geom_smooth()
#p5 <- p5 + my_theme()
#p5

#p5 <- ggplot(exp_ra, aes(x = Ded.cost.prop, y = Avg.detour, color=Appr))
#p5 <- p5 + geom_smooth()
#p5 <- p5 + my_theme()
#p5

#p5 <- ggplot(exp_ra, aes(x = Avg.detour, y = Cost, color=Appr))
#p5 <- p5 + geom_smooth()
#p5 <- p5 + my_theme()
#p5



# ----
# Parameter: driver locations

exp_dl <- fread("csdp_ap_25Aug2019_033043_driver_locations.csv")
exp_dl$Approach <- as.factor(exp_dl$Approach)
exp_dl$Parameter <- as.factor(exp_dl$Parameter)
exp_dl$Seed <- as.factor(exp_dl$Seed)
exp_dl$Zone <- as.factor(exp_dl$Zone)
exp_dl$Distribution <- as.factor(exp_dl$Distribution)

exp_dl[, Ad.hoc.cost.prop := Ad.hoc.cost/Cost]
exp_dl[, Ded.cost.prop := 1 - Ad.hoc.cost.prop]
exp_dl[, Cust.density := Customers/Net.size]
exp_dl[, Stores.density := Stores/Net.size]
exp_dl[, Ad.hoc.serv.cost := Ad.hoc.cost - Ad.hoc.cost/Avg.detour]
exp_dl[, Service.cost.1 := Ad.hoc.serv.cost + Dedicated.cost]
exp_dl[, Ad.hoc.serv.cost.prop := Ad.hoc.serv.cost/Service.cost.1]
exp_dl[, Ded.serv.cost.prop := 1 - Ad.hoc.serv.cost.prop]
exp_dl[, Service.cost.2 := Ad.hoc.serv.cost + 2 * Dedicated.cost]
exp_dl[, Service.cost.3 := Ad.hoc.serv.cost + 3 * Dedicated.cost]
exp_dl[Ad.hoc.serv.cost < 0.1, Ad.hoc.serv.cost := 0]
exp_dl[Approach == "SP-Voronoi-DT", Appr := "Voronoi"]
exp_dl[Approach == "SP-fraction-DT", Appr := paste("Fr: ", Parameter)]
exp_dl[Approach == "SP-threshold-DT", Appr := paste("Thr: ", Parameter)]

p1_dl <- ggplot(exp_dl, aes(x = Distribution, y = Service.cost.1, fill = Appr))
p1_dl <- p1_dl + geom_boxplot()
p1_dl <- p1_dl + scale_x_discrete()
#p1_dl <- p1_dl + scale_y_log10()
#p1_dl <- p1_dl + my_theme()
p1_dl <- p1_dl + labs(x = "Driver location distribution (Start-End)")
p1_dl

p2_dl <- ggplot(exp_dl, aes(x = Distribution, y = Elapsed.time, fill = Appr))
p2_dl <- p2_dl + geom_boxplot()
p2_dl <- p2_dl + scale_x_discrete()
p2_dl <- p2_dl + scale_y_log10()
#p2_dl <- p2_dl + my_theme()
p2_dl <- p2_dl + labs(x = "Driver location distribution (Start-End)")
p2_dl <- p2_dl + labs(y = "Processing time (s)")
p2_dl

p3_dl <- ggplot(exp_dl, aes(x = Distribution, y = Avg.detour, fill = Appr))
p3_dl <- p3_dl + geom_boxplot()
p3_dl <- p3_dl + scale_x_discrete()
#p3_dl <- p3_dl + my_theme()
p3_dl <- p3_dl + labs(x = "Driver location distribution (Start-End)")
p3_dl <- p3_dl + labs(y = "Avg. Detour")
p3_dl

p4_dl <- ggplot(exp_dl, aes(x = Distribution, y = Ded.serv.cost.prop, fill = Appr))
p4_dl <- p4_dl + geom_boxplot()
p4_dl <- p4_dl + scale_x_discrete()
#p4_dl <- p4_dl + my_theme()
p4_dl <- p4_dl + labs(x = "Driver location distribution (Start-End)")
p4_dl <- p4_dl + labs(y = "Prop. Service Cost (Dedicated)")
p4_dl
