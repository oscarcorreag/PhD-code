library(data.table)
library(ggplot2)

setwd("C:/Users/oscarcg/Documents/phd/code/Pickup-Delivery/test/files/")

exp <- fread("populations_22Jul2019_190359.csv")
names(exp)[names(exp) == "V1"] <- "Density"
names(exp)[names(exp) == "V4"] <- "Normalized"
names(exp)[names(exp) == "V5"] <- "Absolute"
exp$Density <- as.factor(exp$Density)
exp$Absolute <- as.factor(exp$Absolute)

p1 <- ggplot(exp[Absolute != 0], aes(x = Absolute, fill = Density))
p1 <- p1 + geom_histogram()
#p1 <- p1 + scale_x_discrete()
p1 <- p1 + labs(y = "Intra-partition density")
p1

p1 <- ggplot(exp[Absolute != 0], aes(x = Normalized, color = Density))
p1 <- p1 + geom_density()
#p1 <- p1 + scale_x_discrete()
p1 <- p1 + labs(y = "Intra-partition density")
p1

p1 <- ggplot(exp[Absolute != 0], aes(x = Absolute, color = Density))
p1 <- p1 + geom_density()
#p1 <- p1 + scale_x_discrete()
p1 <- p1 + labs(y = "Intra-partition density")
p1