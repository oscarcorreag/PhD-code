setwd("C:/Users/oscarcg/Dropbox/Education/Unimelb PhD/code/Hotspot-based/test"),
rs1 <- read.csv("rs1.csv", header = TRUE)
rs2 <- read.csv("rs2.csv", header = TRUE)
rs3 <- read.csv("rs3.csv", header = TRUE)

plot(rs1[,2:4])
cor(rs1[,2:4])
cor.test(rs1$y, rs1$r, method = "pearson")

plot(rs1$rr, rs1$X123)
cor.test(rs1$y, rs1$r, method = "pearson")

