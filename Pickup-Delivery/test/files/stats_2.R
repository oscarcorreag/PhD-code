library(data.table)
library(ggplot2)

setwd("C:/Users/oscarcg/Documents/phd/code/Pickup-Delivery/test/files/")

exp <- fread("csdp_ap_30Aug2019_013156_num_customers.csv")
exp$Ad.hoc.cost.prop <- exp$Ad.hoc.cost / exp$Cost
exp$Ded.cost.prop <- 1 - exp$Ad.hoc.cost.prop
exp$Approach <- as.factor(exp$Approach)
exp$Parameter <- as.factor(exp$Parameter)
exp$Seed <- as.factor(exp$Seed)
exp$Zone <- as.factor(exp$Zone)
exp$Distribution <- as.factor(exp$Distribution)



ratio <- function(sd) {
  baseline <- sd[Approach == "SP-Voronoi-DT", -1, with = FALSE]
  approach <- sd[Approach != "SP-Voronoi-DT", -1, with = FALSE]
  if(nrow(opt) == 1 & nrow(appr) == 1){
    approach[1] / baseline[1]
  }
}


