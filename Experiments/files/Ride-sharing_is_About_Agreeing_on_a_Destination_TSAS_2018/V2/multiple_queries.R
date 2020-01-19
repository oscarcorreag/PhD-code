# setwd("C:/Users/oscarcg/Dropbox/Education/Unimelb PhD/code/Experiments/files/Ride-sharing_is_About_Agreeing_on_a_Destination_TSAS_2018/V2/")
setwd("../Experiments/files/Ride-sharing_is_About_Agreeing_on_a_Destination_TSAS_2018/V2/")

# DATA PRE-PROCESSING ---------------------------------------------------------------------------------------------------------------------

# Retrieve data.
synth.csv <- read.csv("master_synth.csv", header = TRUE)
real.csv <- read.csv("master_real.csv", header = TRUE)

# Convert data frame to data table for filtering and grouping.
library(data.table)

synth_dt <- as.data.table(synth.csv)
real_dt <- as.data.table(real.csv)

# Create new columns and adapt others.
synth_dt$Total.users <- synth_dt$Num.queries * synth_dt$Num.users
synth_dt$Total.POIs <- synth_dt$Num.queries * synth_dt$Num.POIs.query
synth_dt$Ratio.total.users.net <- synth_dt$Total.users / synth_dt$Net.size
synth_dt$Ratio.total.POIs.net <- synth_dt$Total.POIs / synth_dt$Net.size
synth_dt$Ratio.users.queries <- synth_dt$Num.users / synth_dt$Num.queries
synth_dt$Ratio.POIs.users <- synth_dt$Total.POIs / synth_dt$Total.users
synth_dt$Alpha <- as.factor(synth_dt$Alpha)

real_dt$Total.users <- real_dt$Num.queries * real_dt$Num.users
real_dt$Num.POIs.query <- 0
real_dt$Ratio.total.users.net <- real_dt$Total.users / real_dt$Net.size
real_dt$Ratio.total.POIs.net <- real_dt$Total.POIs / real_dt$Net.size
real_dt$Ratio.users.queries <- real_dt$Num.users / real_dt$Num.queries
real_dt$Ratio.POIs.users <- real_dt$Total.POIs / real_dt$Total.users
real_dt$Alpha <- as.factor(real_dt$Alpha)

exp_dt <- rbind(synth_dt, real_dt)

# Group by individual samples and aggregate dependent variables.
# Normalise the dependent variables by considering VST-NCA values as basis.
normalize <- function(sd) {
  ca <- sd[Algorithm == "VST-CA", -1, with = FALSE]
  nca <- sd[Algorithm == "VST-NCA", -1, with = FALSE]
  if(nrow(ca) == 1 & nrow(nca) == 1){
    a <- ca[1, c("Cost", "WARL", "MWRL", "MRL1", "MRL2", "Entropy", "Elapsed.time")] / nca[1, c("Cost", "WARL", "MWRL", "MRL1", "MRL2", "Entropy", "Elapsed.time")]
    b <- ca[1, c("Num.it")]
    c(a, b)
  }
}

by_cols <- c("Net.size", "Cap", "Merge.cells", "Num.queries", "Num.users.query", "Total.POIs", "POIs.dist", "Alpha", "Beta", "Ratio.total.users.net", "Ratio.total.POIs.net", "Ratio.POIs.users", "Ratio.users.queries", "Sample")
sd_cols <- c("Algorithm", "Cost", "WARL", "MWRL", "MRL1", "MRL2", "Entropy", "Elapsed.time", "Num.it")

pure <- exp_dt[Strategy == "N/A" | Strategy == "pure", normalize(.SD), by = by_cols, .SDcols = sd_cols]
pure$Strategy <- "Pure"

mixed <- exp_dt[Strategy == "N/A" | Strategy == "mixed", normalize(.SD), by = by_cols, .SDcols = sd_cols]
mixed$Strategy <- "Mixed"

# Merge strategies.
exp_dt_2 <- rbind(pure, mixed)

# Merge proportions with actual values.
exp_dt_3 <- merge(exp_dt[Algorithm == "VST-NCA"], exp_dt_2, by = by_cols)

# Columns that show whether VST-CA had effect on congestion in terms of COST.
exp_dt_3$Effect.Cost <- rep("", nrow(exp_dt_3))
exp_dt_3[Cost.y > 1.0, Effect.Cost := "(-)"]
exp_dt_3[Cost.y == 1.0, Effect.Cost := "0%"]
exp_dt_3[Cost.y < 1.0 & Cost.y > 0.95, Effect.Cost := "< 5%"]
exp_dt_3[Cost.y <= 0.95 & Cost.y >= 0.9, Effect.Cost := "5% - 10%"]
exp_dt_3[Cost.y < 0.9, Effect.Cost := "> 10%"]
exp_dt_3$Effect.Cost <- factor(exp_dt_3$Effect.Cost)
exp_dt_3$Effect.Cost <- factor(exp_dt_3$Effect.Cost, levels(exp_dt_3$Effect.Cost)[c(3, 5, 2, 4, 1)])

exp_dt_3$Type.Effect.Cost <- rep("", nrow(exp_dt_3))
exp_dt_3[Cost.y < 1.0, Type.Effect.Cost := "Reduction"]
exp_dt_3[Cost.y == 1.0, Type.Effect.Cost := "No reduction"]
exp_dt_3[Cost.y > 1.0, Type.Effect.Cost := "(-) reduction"]
exp_dt_3$Type.Effect.Cost <- factor(exp_dt_3$Type.Effect.Cost)
exp_dt_3$Type.Effect.Cost <- factor(exp_dt_3$Type.Effect.Cost, levels(exp_dt_3$Type.Effect.Cost)[c(2, 3, 1)])

exp_dt_3$Type.Net <- rep("", nrow(exp_dt_3))
exp_dt_3[POIs.dist %in% c("uniform", "zipfian"), Type.Net := "Synthetic"]
exp_dt_3[POIs.dist %in% c("Manhattan", "Melbourne", "Quito"), Type.Net := "Real"]
exp_dt_3$Type.Net <- factor(exp_dt_3$Type.Net)


synth <- exp_dt_3[Type.Net == "Synthetic"]
synth$POIs.dist <- droplevels(synth$POIs.dist)

#synth$Ratio.POIs.users <- as.factor(synth$Ratio.POIs.users)

synth$Levels.r.users.net <- rep("", nrow(synth))
synth[Ratio.total.users.net <= 0.02, Levels.r.users.net := "[0.00, 0.02]"]
synth[Ratio.total.users.net > 0.02 & Ratio.total.users.net <= 0.04, Levels.r.users.net := "(0.02, 0.04]"]
synth[Ratio.total.users.net > 0.04 & Ratio.total.users.net <= 0.08, Levels.r.users.net := "(0.04, 0.08]"]
synth[Ratio.total.users.net > 0.08 & Ratio.total.users.net <= 0.16, Levels.r.users.net := "(0.08, 0.16]"]
synth[Ratio.total.users.net > 0.16 & Ratio.total.users.net <= 0.32, Levels.r.users.net := "(0.16, 0.32]"]
synth[Ratio.total.users.net > 0.32 & Ratio.total.users.net <= 0.64, Levels.r.users.net := "(0.32, 0.64]"]
synth$Levels.r.users.net <- as.factor(synth$Levels.r.users.net)
synth$Levels.r.users.net <- factor(synth$Levels.r.users.net, levels(synth$Levels.r.users.net)[c(6, 1, 2, 3, 4, 5)])

synth$Levels.r.pois.net <- rep("", nrow(synth))
synth[Ratio.total.POIs.net <= 0.01, Levels.r.pois.net := "[0, 0.01]"]
synth[Ratio.total.POIs.net > 0.01 & Ratio.total.POIs.net <= 0.02,  Levels.r.pois.net := "(0.01, 0.02]"]
synth[Ratio.total.POIs.net > 0.02 & Ratio.total.POIs.net <= 0.03,  Levels.r.pois.net := "(0.02, 0.03]"]
synth[Ratio.total.POIs.net > 0.03 & Ratio.total.POIs.net <= 0.04,  Levels.r.pois.net := "(0.03, 0.04]"]
synth$Levels.r.pois.net <- as.factor(synth$Levels.r.pois.net)
synth$Levels.r.pois.net <- factor(synth$Levels.r.pois.net, levels(synth$Levels.r.pois.net)[c(4, 1, 2, 3)])

synth$Levels.warl.x <- rep("", nrow(synth))
synth[WARL.x <= 0.06, Levels.warl.x := "[0, 0.06]"]
synth[WARL.x > 0.06 & WARL.x <= 0.10, Levels.warl.x := "(0.06, 0.10]"]
synth[WARL.x > 0.10 & WARL.x <= 0.14, Levels.warl.x := "(0.10, 0.14]"]
synth[WARL.x > 0.14 & WARL.x <= 0.18, Levels.warl.x := "(0.14, 0.18]"]
synth[WARL.x > 0.18 & WARL.x <= 0.22, Levels.warl.x := "(0.18, 0.22]"]
synth$Levels.warl.x <- as.factor(synth$Levels.warl.x)
synth$Levels.warl.x <- factor(synth$Levels.warl.x, levels(synth$Levels.warl.x)[c(5, 1, 2, 3, 4)])


real <- exp_dt_3[Type.Net == "Real"]
real$POIs.dist <- droplevels(real$POIs.dist)

real$Levels.r.pois.u <- rep("", nrow(real))
real[Ratio.POIs.users <= 1.0, Levels.r.pois.u := "[0.0, 1.0]"]
real[Ratio.POIs.users > 1.0 & Ratio.POIs.users <= 2.0, Levels.r.pois.u := "(1.0, 2.0]"]
real[Ratio.POIs.users > 2.0 & Ratio.POIs.users <= 3.0, Levels.r.pois.u := "(2.0, 3.0]"]
real[Ratio.POIs.users > 3.0 & Ratio.POIs.users <= 5.0, Levels.r.pois.u := "(3.0, 5.0]"]
real$Levels.r.pois.u <- as.factor(real$Levels.r.pois.u)
real$Levels.r.pois.u <- factor(real$Levels.r.pois.u, levels(real$Levels.r.pois.u)[c(4, 1, 2, 3)])

real$Levels.r.users.net <- rep("", nrow(real))
real[Ratio.total.users.net <= 0.2, Levels.r.users.net := "[0.0, 0.2]"]
real[Ratio.total.users.net > 0.2 & Ratio.total.users.net <= 0.4, Levels.r.users.net := "(0.2, 0.4]"]
real[Ratio.total.users.net > 0.4 & Ratio.total.users.net <= 0.6, Levels.r.users.net := "(0.4, 0.6]"]
real[Ratio.total.users.net > 0.6 & Ratio.total.users.net <= 0.8, Levels.r.users.net := "(0.6, 0.8]"]
real[Ratio.total.users.net > 0.8 & Ratio.total.users.net <= 1.0, Levels.r.users.net := "(0.8, 1.0]"]
real$Levels.r.users.net <- as.factor(real$Levels.r.users.net)
real$Levels.r.users.net <- factor(real$Levels.r.users.net, levels(real$Levels.r.users.net)[c(5, 1, 2, 3, 4)])

real$Levels.r.pois.net <- rep("", nrow(real))
real[Ratio.total.POIs.net <= 0.1,  Levels.r.pois.net := "[0, 0.1]"]
real[Ratio.total.POIs.net > 0.1 & Ratio.total.POIs.net <= 0.2,  Levels.r.pois.net := "(0.1, 0.2]"]
real[Ratio.total.POIs.net > 0.2 & Ratio.total.POIs.net <= 0.3,  Levels.r.pois.net := "(0.2, 0.3]"]
real[Ratio.total.POIs.net > 0.3 & Ratio.total.POIs.net <= 0.5,  Levels.r.pois.net := "(0.3, 0.5]"]
real$Levels.r.pois.net <- as.factor(real$Levels.r.pois.net)
real$Levels.r.pois.net <- factor(real$Levels.r.pois.net, levels(real$Levels.r.pois.net)[c(4, 1, 2, 3)])

real$Levels.warl.x <- rep("", nrow(real))
real[WARL.x <= 0.2, Levels.warl.x := "[0, 0.2]"]
real[WARL.x > 0.2 & WARL.x <= 0.4, Levels.warl.x := "(0.2, 0.4]"]
real[WARL.x > 0.4 & WARL.x <= 0.8, Levels.warl.x := "(0.4, 0.8]"]
real[WARL.x > 0.8 & WARL.x <= 2.4, Levels.warl.x := "(0.8, 2.4]"]
real$Levels.warl.x <- as.factor(real$Levels.warl.x)
real$Levels.warl.x <- factor(real$Levels.warl.x, levels(real$Levels.warl.x)[c(4, 1, 2, 3)])


# STATISTICS (SYNTH) ----------------------------------------------------------------------------------------------------------------------

# Proportions by factor within each categorical variable
prop.table(table(synth$Effect.Cost, synth$POIs.dist), 1)
prop.table(table(synth$Effect.Cost, synth$Alpha), 1)
prop.table(table(synth$Effect.Cost, synth$Strategy.y), 1)
prop.table(table(synth$Effect.Cost, synth$Levels.r.users.net), 1)
prop.table(table(synth$Effect.Cost, synth$Levels.r.pois.net), 1)
prop.table(table(synth$Effect.Cost, synth$Levels.warl.x), 1)

prop.table(table(synth$Effect.Cost, synth$POIs.dist), 2)
prop.table(table(synth$Effect.Cost, synth$Alpha), 2)
prop.table(table(synth$Effect.Cost, synth$Levels.r.users.net), 2)
prop.table(table(synth$Effect.Cost, synth$Levels.r.pois.net), 2)
prop.table(table(synth$Effect.Cost, synth$Levels.warl.x), 2)


synth_no_obs_by_eff_cost <- data.table(table(synth$Effect.Cost))
names(synth_no_obs_by_eff_cost) <- c("Effect.Cost", "Count")
synth_no_obs_by_eff_cost$Effect.Cost <- as.factor(synth_no_obs_by_eff_cost$Effect.Cost)

# Weighted average of proportions which have positive effect on the cost (cost reduction).
synth_weights_w_eff_cost <- c(synth_no_obs_by_eff_cost[Effect.Cost %in% c("> 10%", "5% - 10%", "< 5%"), Count], c(0, 0))

# Weighted average of proportions which have negative or no effect on the cost (cost reduction).
synth_weights_wo_eff_cost <- c(c(0, 0, 0), synth_no_obs_by_eff_cost[Effect.Cost %in% c("0%", "(-)"), Count])

synth_prop_pois_dist <- matrix(prop.table(table(synth$Effect.Cost, synth$POIs.dist), 1), ncol=2)
synth_prop_alpha <- matrix(prop.table(table(synth$Effect.Cost, synth$Alpha), 1), ncol=3)
synth_prop_strategy <- matrix(prop.table(table(synth$Effect.Cost, synth$Strategy.y), 1), ncol=2)
synth_prop_run <- matrix(prop.table(table(synth$Effect.Cost, synth$Levels.r.users.net), 1), ncol=6)
synth_prop_rpn <- matrix(prop.table(table(synth$Effect.Cost, synth$Levels.r.pois.net), 1), ncol=4)
synth_prop_rpu <- matrix(prop.table(table(synth$Effect.Cost, synth$Ratio.POIs.users), 1), ncol=4)
synth_prop_warl.x <- matrix(prop.table(table(synth$Effect.Cost, synth$Levels.warl.x), 1), ncol=5)

library(questionr)

# Weighted averages for POSITIVE REDUCTION.
wtd.mean(synth_prop_pois_dist[,1], synth_weights_w_eff_cost)
wtd.mean(synth_prop_pois_dist[,2], synth_weights_w_eff_cost)
wtd.mean(synth_prop_alpha[,1], synth_weights_w_eff_cost)
wtd.mean(synth_prop_alpha[,2], synth_weights_w_eff_cost)
wtd.mean(synth_prop_alpha[,3], synth_weights_w_eff_cost)
wtd.mean(synth_prop_strategy[,1], synth_weights_w_eff_cost)
wtd.mean(synth_prop_strategy[,2], synth_weights_w_eff_cost)
wtd.mean(synth_prop_run[,1], synth_weights_w_eff_cost)
wtd.mean(synth_prop_run[,2], synth_weights_w_eff_cost)
wtd.mean(synth_prop_run[,3], synth_weights_w_eff_cost)
wtd.mean(synth_prop_run[,4], synth_weights_w_eff_cost)
wtd.mean(synth_prop_run[,5], synth_weights_w_eff_cost)
wtd.mean(synth_prop_run[,6], synth_weights_w_eff_cost)
wtd.mean(synth_prop_rpn[,1], synth_weights_w_eff_cost)
wtd.mean(synth_prop_rpn[,2], synth_weights_w_eff_cost)
wtd.mean(synth_prop_rpn[,3], synth_weights_w_eff_cost)
wtd.mean(synth_prop_rpn[,4], synth_weights_w_eff_cost)
wtd.mean(synth_prop_warl.x[,1], synth_weights_w_eff_cost)
wtd.mean(synth_prop_warl.x[,2], synth_weights_w_eff_cost)
wtd.mean(synth_prop_warl.x[,3], synth_weights_w_eff_cost)
wtd.mean(synth_prop_warl.x[,4], synth_weights_w_eff_cost)
wtd.mean(synth_prop_warl.x[,5], synth_weights_w_eff_cost)

# Weighted averages for NEGATIVE OR NO REDUCTION.
wtd.mean(synth_prop_pois_dist[,1], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_pois_dist[,2], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_alpha[,1], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_alpha[,2], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_alpha[,3], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_strategy[,1], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_strategy[,2], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_run[,1], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_run[,2], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_run[,3], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_run[,4], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_run[,5], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_run[,6], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_rpn[,1], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_rpn[,2], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_rpn[,3], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_rpn[,4], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_rpu[,1], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_rpu[,2], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_rpu[,3], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_rpu[,4], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_warl.x[,1], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_warl.x[,2], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_warl.x[,3], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_warl.x[,4], synth_weights_wo_eff_cost)
wtd.mean(synth_prop_warl.x[,5], synth_weights_wo_eff_cost)

# TO SOLVE -----
# Find interaction between variables for reduction of cost.
#synth.reduced.cost <- synth[Effect.Cost %in% c("> 10%", "5% - 10%", "< 5%")]
synth.reduced.cost <- synth[Type.Effect.Cost == "Reduction"]
synth.reduced.cost$Effect.Cost <- droplevels(synth.reduced.cost$Effect.Cost)

synth.pois.dist.reduced.cost.table <- table(synth.reduced.cost$POIs.dist, synth.reduced.cost$Effect.Cost)
synth.alpha.reduced.cost.table <- table(synth.reduced.cost$Alpha, synth.reduced.cost$Effect.Cost)
synth.strategy.reduced.cost.table <- table(synth.reduced.cost$Strategy.y, synth.reduced.cost$Effect.Cost)
synth.rpn.reduced.cost.table <- table(synth.reduced.cost$Levels.r.pois.net, synth.reduced.cost$Effect.Cost)
synth.rpu.reduced.cost.table <- table(synth.reduced.cost$Ratio.POIs.users, synth.reduced.cost$Effect.Cost)
synth.warl.x.reduced.cost.table <- table(synth.reduced.cost$Levels.warl.x, synth.reduced.cost$Effect.Cost)

chisq.test(synth.pois.dist.reduced.cost.table)
chisq.test(synth.alpha.reduced.cost.table)
chisq.test(synth.strategy.reduced.cost.table)
chisq.test(synth.rpn.reduced.cost.table, simulate.p.value = TRUE)
chisq.test(synth.rpu.reduced.cost.table, simulate.p.value = TRUE)
chisq.test(synth.warl.x.reduced.cost.table, simulate.p.value = TRUE)

library(stats)

interaction.plot(synth.reduced.cost$POIs.dist, synth.reduced.cost$Alpha, synth.reduced.cost$Cost.y)
interaction.plot(synth.reduced.cost$POIs.dist, synth.reduced.cost$Levels.r.pois.net, synth.reduced.cost$Cost.y)
interaction.plot(synth.reduced.cost$POIs.dist, synth.reduced.cost$Ratio.POIs.users, synth.reduced.cost$Cost.y)
interaction.plot(synth.reduced.cost$POIs.dist, synth.reduced.cost$Levels.warl.x, synth.reduced.cost$Cost.y)

interaction.plot(synth.reduced.cost$Alpha, synth.reduced.cost$Levels.r.pois.net, synth.reduced.cost$Cost.y)
interaction.plot(synth.reduced.cost$Alpha, synth.reduced.cost$Ratio.POIs.users, synth.reduced.cost$Cost.y)  # YES!
interaction.plot(synth.reduced.cost$Alpha, synth.reduced.cost$Levels.warl.x, synth.reduced.cost$Cost.y)

interaction.plot(synth.reduced.cost$Levels.r.pois.net, synth.reduced.cost$Ratio.POIs.users, synth.reduced.cost$Cost.y)  # YES!
interaction.plot(synth.reduced.cost$Levels.r.pois.net, synth.reduced.cost$Levels.warl.x, synth.reduced.cost$Cost.y)

interaction.plot(synth.reduced.cost$Ratio.POIs.users, synth.reduced.cost$Levels.warl.x, synth.reduced.cost$Cost.y)


synth.reduced.cost.lm <- lm(Cost.y ~ POIs.dist + Alpha + Strategy.y + Levels.r.pois.net + Ratio.POIs.users + Levels.warl.x, data = synth.reduced.cost)
anova(synth.reduced.cost.lm)

synth.reduced.cost.lm.1 <- lm(Cost.y ~ POIs.dist + Alpha + Strategy.y + Levels.r.pois.net + Levels.warl.x, data = synth.reduced.cost)
anova(synth.reduced.cost.lm.1)

synth.reduced.cost.lm.2 <- lm(Cost.y ~ POIs.dist + Alpha + Levels.r.pois.net + Levels.warl.x, data = synth.reduced.cost)
anova(synth.reduced.cost.lm.2)

synth.reduced.cost.lm.3 <- lm(Cost.y ~ Alpha * Ratio.POIs.users, data = synth.reduced.cost)
anova(synth.reduced.cost.lm.3)


# STATISTICS (REAL) -----------------------------------------------------------------------------------------------------------------------

# Proportions by factor within each categorical variable
prop.table(table(real$Effect.Cost, real$POIs.dist), 1)
prop.table(table(real$Effect.Cost, real$Alpha), 1)
prop.table(table(real$Effect.Cost, real$Strategy.y), 1)
prop.table(table(real$Effect.Cost, real$Levels.r.users.net), 1)
prop.table(table(real$Effect.Cost, real$Levels.r.pois.net), 1)
prop.table(table(real$Effect.Cost, real$Levels.warl.x), 1)

prop.table(table(real$Effect.Cost, real$POIs.dist), 2)
prop.table(table(real$Effect.Cost, real$Levels.r.users.net), 2)
prop.table(table(real$Effect.Cost, real$Levels.r.pois.net), 2)
prop.table(table(real$Effect.Cost, real$Levels.warl.x), 2)


real_no_obs_by_eff_cost <- data.table(table(real$Effect.Cost))
names(real_no_obs_by_eff_cost) <- c("Effect.Cost", "Count")
real_no_obs_by_eff_cost$Effect.Cost <- as.factor(real_no_obs_by_eff_cost$Effect.Cost)

# Weighted average of proportions which have positive effect on the cost (cost reduction).
real_weights_w_eff_cost <- c(real_no_obs_by_eff_cost[Effect.Cost %in% c("> 10%", "5% - 10%", "< 5%"), Count], c(0, 0))

# Weighted average of proportions which have negative or no effect on the cost (cost reduction).
real_weights_wo_eff_cost <- c(c(0, 0, 0), real_no_obs_by_eff_cost[Effect.Cost %in% c("0%", "(-)"), Count])

real_prop_pois_dist <- matrix(prop.table(table(real$Effect.Cost, real$POIs.dist), 1), ncol=3)
real_prop_strategy <- matrix(prop.table(table(real$Effect.Cost, real$Strategy.y), 1), ncol=2)
real_prop_run <- matrix(prop.table(table(real$Effect.Cost, real$Levels.r.users.net), 1), ncol=5)
real_prop_rpn <- matrix(prop.table(table(real$Effect.Cost, real$Levels.r.pois.net), 1), ncol=4)
real_prop_rpu <- matrix(prop.table(table(real$Effect.Cost, real$Levels.r.pois.u), 1), ncol=4)
real_prop_warl.x <- matrix(prop.table(table(real$Effect.Cost, real$Levels.warl.x), 1), ncol=4)

library(questionr)

# Weighted averages for POSITIVE REDUCTION.
wtd.mean(real_prop_pois_dist[,1], real_weights_w_eff_cost)
wtd.mean(real_prop_pois_dist[,2], real_weights_w_eff_cost)
wtd.mean(real_prop_pois_dist[,3], real_weights_w_eff_cost)
wtd.mean(real_prop_strategy[,1], real_weights_w_eff_cost)
wtd.mean(real_prop_strategy[,2], real_weights_w_eff_cost)
wtd.mean(real_prop_run[,1], real_weights_w_eff_cost)
wtd.mean(real_prop_run[,2], real_weights_w_eff_cost)
wtd.mean(real_prop_run[,3], real_weights_w_eff_cost)
wtd.mean(real_prop_run[,4], real_weights_w_eff_cost)
wtd.mean(real_prop_run[,5], real_weights_w_eff_cost)
wtd.mean(real_prop_rpn[,1], real_weights_w_eff_cost)
wtd.mean(real_prop_rpn[,2], real_weights_w_eff_cost)
wtd.mean(real_prop_rpn[,3], real_weights_w_eff_cost)
wtd.mean(real_prop_rpn[,4], real_weights_w_eff_cost)
wtd.mean(real_prop_warl.x[,1], real_weights_w_eff_cost)
wtd.mean(real_prop_warl.x[,2], real_weights_w_eff_cost)
wtd.mean(real_prop_warl.x[,3], real_weights_w_eff_cost)
wtd.mean(real_prop_warl.x[,4], real_weights_w_eff_cost)

# Weighted averages for NEGATIVE OR NO REDUCTION.
wtd.mean(real_prop_pois_dist[,1], real_weights_wo_eff_cost)
wtd.mean(real_prop_pois_dist[,2], real_weights_wo_eff_cost)
wtd.mean(real_prop_pois_dist[,3], real_weights_wo_eff_cost)
wtd.mean(real_prop_strategy[,1], real_weights_wo_eff_cost)
wtd.mean(real_prop_strategy[,2], real_weights_wo_eff_cost)
wtd.mean(real_prop_run[,1], real_weights_wo_eff_cost)
wtd.mean(real_prop_run[,2], real_weights_wo_eff_cost)
wtd.mean(real_prop_run[,3], real_weights_wo_eff_cost)
wtd.mean(real_prop_run[,4], real_weights_wo_eff_cost)
wtd.mean(real_prop_run[,5], real_weights_wo_eff_cost)
wtd.mean(real_prop_rpn[,1], real_weights_wo_eff_cost)
wtd.mean(real_prop_rpn[,2], real_weights_wo_eff_cost)
wtd.mean(real_prop_rpn[,3], real_weights_wo_eff_cost)
wtd.mean(real_prop_rpn[,4], real_weights_wo_eff_cost)
wtd.mean(real_prop_rpu[,1], real_weights_wo_eff_cost)
wtd.mean(real_prop_rpu[,2], real_weights_wo_eff_cost)
wtd.mean(real_prop_rpu[,3], real_weights_wo_eff_cost)
wtd.mean(real_prop_rpu[,4], real_weights_wo_eff_cost)
wtd.mean(real_prop_warl.x[,1], real_weights_wo_eff_cost)
wtd.mean(real_prop_warl.x[,2], real_weights_wo_eff_cost)
wtd.mean(real_prop_warl.x[,3], real_weights_wo_eff_cost)
wtd.mean(real_prop_warl.x[,4], real_weights_wo_eff_cost)





# Find interaction between variables for reduction of cost.
#real.reduced.cost <- real[Effect.Cost %in% c("> 10%", "5% - 10%", "< 5%")]
real.reduced.cost <- real[Type.Effect.Cost == "Reduction"]
real.reduced.cost$Effect.Cost <- droplevels(real.reduced.cost$Effect.Cost)

real.pois.dist.reduced.cost.table <- table(real.reduced.cost$POIs.dist, real.reduced.cost$Effect.Cost)
#real.alpha.reduced.cost.table <- table(real.reduced.cost$Alpha, real.reduced.cost$Effect.Cost)
real.strategy.reduced.cost.table <- table(real.reduced.cost$Strategy.y, real.reduced.cost$Effect.Cost)
real.rpn.reduced.cost.table <- table(real.reduced.cost$Levels.r.pois.net, real.reduced.cost$Effect.Cost)
real.rpu.reduced.cost.table <- table(real.reduced.cost$Levels.r.pois.u, real.reduced.cost$Effect.Cost)
real.warl.x.reduced.cost.table <- table(real.reduced.cost$Levels.warl.x, real.reduced.cost$Effect.Cost)

chisq.test(real.pois.dist.reduced.cost.table)
#chisq.test(real.alpha.reduced.cost.table)
chisq.test(real.strategy.reduced.cost.table)
chisq.test(real.rpn.reduced.cost.table, simulate.p.value = TRUE)
chisq.test(real.rpu.reduced.cost.table, simulate.p.value = TRUE)
chisq.test(real.warl.x.reduced.cost.table, simulate.p.value = TRUE)



# PLOTS -----------------------------------------------------------------------------------------------------------------------------------
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
      legend.justification = c(1, 0),
      legend.position      = c(1, 0),
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

# TO SHOW WHETHER COST REDUCTION WAS POSSIBLE FOR EACH TYPE OF NETWORK. -------------------------------------------------------------------

# Proportions of the [type of effect on cost] by [type of network].
prop.type.eff.cost.type.net <- data.table(prop.table(table(exp_dt_3$Type.Net, exp_dt_3$Type.Effect.Cost), 1))
names(prop.type.eff.cost.type.net) <- c("Type.Net", "Type.Effect.Cost", "Prop")
prop.type.eff.cost.type.net$Type.Net <- factor(prop.type.eff.cost.type.net$Type.Net)
prop.type.eff.cost.type.net$Type.Effect.Cost <- factor(prop.type.eff.cost.type.net$Type.Effect.Cost)
prop.type.eff.cost.type.net$Type.Effect.Cost <- factor(prop.type.eff.cost.type.net$Type.Effect.Cost, levels(prop.type.eff.cost.type.net$Type.Effect.Cost)[c(2, 3, 1)])

p1 <- ggplot(prop.type.eff.cost.type.net[Type.Effect.Cost %in% c("Reduction", "No reduction")], aes(x = Type.Effect.Cost, y = Prop, fill = Type.Net))
p1 <- p1 + geom_bar(stat = 'identity', position = 'dodge')
p1 <- p1 + my_theme()
p1 <- p1 + theme(legend.position = c(1, 1), legend.justification = c(1, 1), axis.title.x = element_text(size = 14, vjust = 0.5, face="plain"))
p1 <- p1 + labs(x = "(a)", y = "Proportion of Samples")
p1 <- p1 + guides(fill = guide_legend(title = "Network type"))
p1 <- p1 + theme(axis.title.y = element_text(margin = margin(t = 0, r = 8, b = 0, l = 0)))
p1

# Proportions of the [type of effect on cost] by [distribution of POIs] in REAL networks.
prop.type.eff.cost.real <- data.table(prop.table(table(real$POIs.dist, real$Type.Effect.Cost), 1))
names(prop.type.eff.cost.real) <- c("POIs.dist", "Type.Effect.Cost", "Prop")
prop.type.eff.cost.real$POIs.dist <- factor(prop.type.eff.cost.real$POIs.dist)
prop.type.eff.cost.real$Type.Effect.Cost <- factor(prop.type.eff.cost.real$Type.Effect.Cost)
prop.type.eff.cost.real$Type.Effect.Cost <- factor(prop.type.eff.cost.real$Type.Effect.Cost, levels(prop.type.eff.cost.real$Type.Effect.Cost)[c(2, 3, 1)])

p2 <- ggplot(prop.type.eff.cost.real[Type.Effect.Cost %in% c("Reduction", "No reduction")], aes(x = Type.Effect.Cost, y = Prop, fill = POIs.dist))
p2 <- p2 + geom_bar(stat = 'identity', position = 'dodge')
p2 <- p2 + my_theme()
p2 <- p2 + theme(legend.position = c(1, 1), legend.justification = c(1, 1), axis.title.x = element_text(size = 14, vjust = 0.5, face="plain"))
p2 <- p2 + labs(x = "(b)", y = "Proportion of Samples")
p2 <- p2 + guides(fill = guide_legend(title = "City (Borough)"))
p2 <- p2 + theme(axis.title.y = element_text(margin = margin(t = 0, r = 8, b = 0, l = 0)))
p2

# Proportions of the [type of effect on cost] by [distribution of POIs] in SYNTHETIC networks.
prop.type.eff.cost.synth <- data.table(prop.table(table(synth$POIs.dist, synth$Type.Effect.Cost), 1))
names(prop.type.eff.cost.synth) <- c("POIs.dist", "Type.Effect.Cost", "Prop")
prop.type.eff.cost.synth$POIs.dist <- factor(prop.type.eff.cost.synth$POIs.dist)
prop.type.eff.cost.synth$Type.Effect.Cost <- factor(prop.type.eff.cost.synth$Type.Effect.Cost)
prop.type.eff.cost.synth$Type.Effect.Cost <- factor(prop.type.eff.cost.synth$Type.Effect.Cost, levels(prop.type.eff.cost.synth$Type.Effect.Cost)[c(2, 3, 1)])

p3 <- ggplot(prop.type.eff.cost.synth[Type.Effect.Cost %in% c("Reduction", "No reduction")], aes(x = Type.Effect.Cost, y = Prop, fill = POIs.dist))
p3 <- p3 + geom_bar(stat = 'identity', position = 'dodge')
p3 <- p3 + my_theme()
p3 <- p3 + theme(legend.position = c(1, 0), legend.justification = c(1, 0), axis.title.x = element_text(size = 14, vjust = 0.5, face="plain"))
p3 <- p3 + scale_fill_manual(values = alpha(c("blue", "red"), .5))
p3 <- p3 + labs(x = "(c)", y = "Proportion of Samples")
p3 <- p3 + guides(fill = guide_legend(title = "POIs distribution"))
p3 <- p3 + theme(axis.title.y = element_text(margin = margin(t = 0, r = 8, b = 0, l = 0)))
p3

multiplot(p1, p2, p3, cols = 3)

# TO SHOW THE INFLUENCE OF THE LEVEL OF CONGESTION (WARL.X) OVER COST REDUCTION. ----------------------------------------------------------
real.warl.x.lims.good.red <- boxplot.stats(real[Effect.Cost == "> 10%", WARL.x])$stats[c(1, 5)]

p1 <- ggplot(real[Type.Effect.Cost %in% c("Reduction", "No reduction")], aes(x=WARL.x, y=Cost.y, colour=Effect.Cost))
p1 <- p1 + geom_jitter()
p1 <- p1 + my_theme()
p1 <- p1 + labs(x = "WARL", y = "Proportion of VST-RS Cost")
p1 <- p1 + theme(axis.title.y = element_text(margin = margin(t = 0, r = 36, b = 0, l = 0)))
p1 <- p1 + geom_vline(xintercept=real.warl.x.lims.good.red[1], linetype="twodash", color = "black")
p1 <- p1 + geom_vline(xintercept=real.warl.x.lims.good.red[2], linetype="twodash", color = "black")
p1

p2 <- ggplot(real[Type.Effect.Cost %in% c("Reduction", "No reduction")], aes(x=Effect.Cost, y=WARL.x, fill=Effect.Cost))
p2 <- p2 + geom_boxplot(varwidth = TRUE)
p2 <- p2 + my_theme()
p2 <- p2 + labs(x = "Reduction of Travel Cost", y = "WARL")
p2 <- p2 + theme(axis.title.y = element_text(margin = margin(t = 0, r = 15, b = 0, l = 0)))
p2 <- p2 + geom_hline(yintercept=real.warl.x.lims.good.red[1], linetype="twodash", color = "black")
p2 <- p2 + geom_hline(yintercept=real.warl.x.lims.good.red[2], linetype="twodash", color = "black")
p2 <- p2 + coord_flip()
p2

synth.warl.x.lims.good.red <- boxplot.stats(synth[Effect.Cost == "> 10%", WARL.x])$stats[c(1, 5)]

p3 <- ggplot(synth[Type.Effect.Cost %in% c("Reduction", "No reduction")], aes(x=WARL.x, y=Cost.y, colour=Effect.Cost))
p3 <- p3 + geom_jitter()
p3 <- p3 + my_theme()
p3 <- p3 + labs(x = "WARL", y = "Proportion of VST-RS Cost")
p3 <- p3 + theme(axis.title.y = element_text(margin = margin(t = 0, r = 36, b = 0, l = 0)))
p3 <- p3 + geom_vline(xintercept=synth.warl.x.lims.good.red[1], linetype="twodash", color = "black")
p3 <- p3 + geom_vline(xintercept=synth.warl.x.lims.good.red[2], linetype="twodash", color = "black")
p3

p4 <- ggplot(synth[Type.Effect.Cost %in% c("Reduction", "No reduction")], aes(x=Effect.Cost, y=WARL.x, fill=Effect.Cost))
p4 <- p4 + geom_boxplot(varwidth = TRUE)
p4 <- p4 + my_theme()
p4 <- p4 + labs(x = "Reduction of Travel Cost", y = "WARL")
p4 <- p4 + theme(axis.title.y = element_text(margin = margin(t = 0, r = 15, b = 0, l = 0)))
p4 <- p4 + geom_hline(yintercept=synth.warl.x.lims.good.red[1], linetype="twodash", color = "black")
p4 <- p4 + geom_hline(yintercept=synth.warl.x.lims.good.red[2], linetype="twodash", color = "black")
p4 <- p4 + coord_flip()
p4

multiplot(p1, p2, p3, p4, cols = 2)


# TO SHOW THE INFLUENCE OF THE RATIOs OF THE NUMBER OF POIS|USERS TO THE SIZE OF THE NETWORK OVER COST REDUCTION. -------------------------

p3 <- ggplot(real[Type.Effect.Cost %in% c("Reduction", "No reduction")], aes(x=Ratio.total.users.net, fill=POIs.dist))
#p3 <- p3 + geom_density(alpha=.3, size=1.2, aes(y = ..count..))
p3 <- p3 + geom_histogram(position = "dodge", bins = 10)
#p3 <- p3 + scale_linetype_manual(values=c("dashed", "dotted", "solid"))
p3 <- p3 + my_theme()
p3 <- p3 + theme(legend.position = c(1, 1), legend.justification = c(1, 1))
p3 <- p3 + theme(axis.title.y = element_text(margin = margin(t = 0, r = 8, b = 0, l = 0)))
p3 <- p3 + labs(x = "User density", y = "# Samples")
p3 <- p3 + guides(fill = guide_legend(title = "City (Borough)"))
p3

p1 <- ggplot(real[Type.Effect.Cost %in% c("Reduction", "No reduction")], aes(x=Ratio.total.POIs.net, fill=POIs.dist))
#p1 <- p1 + geom_density(alpha=.3, size=1.2, aes(y = ..count..))
p1 <- p1 + geom_histogram(position = "dodge", bins = 10)
#p1 <- p1 + scale_linetype_manual(values=c("dashed", "dotted", "solid"))
p1 <- p1 + my_theme()
p1 <- p1 + theme(legend.position = c(1, 1), legend.justification = c(1, 1))
p1 <- p1 + theme(axis.title.y = element_text(margin = margin(t = 0, r = 8, b = 0, l = 0)))
p1 <- p1 + labs(x = "POI density", y = "# Samples")
p1 <- p1 + guides(fill = guide_legend(title = "City (Borough)"))
p1

p2 <- ggplot(real[Type.Effect.Cost %in% c("Reduction", "No reduction")], aes(x=Ratio.POIs.users, fill=POIs.dist))
#p2 <- p2 + geom_density(alpha=.3, size=0.7)
p2 <- p2 + geom_histogram(position = "dodge", bins = 10)
#p2 <- p2 + scale_linetype_manual(values=c("dashed", "dotted", "solid"))
p2 <- p2 + my_theme()
p2 <- p2 + theme(legend.position = c(1, 1), legend.justification = c(1, 1))
p2 <- p2 + theme(axis.title.y = element_text(margin = margin(t = 0, r = 8, b = 0, l = 0)))
p2 <- p2 + labs(x = "# POIs / # Users", y = "# Samples")
p2 <- p2 + guides(fill = guide_legend(title = "City (Borough)"))
p2

multiplot(p3, p1, p2, cols = 3)


# TO SHOW THE BEHAVIOR OF MIXED VS PURE STRATEGIES ----------------------------------------------------------------------------------------
table(real[Type.Effect.Cost %in% c("Reduction", "No reduction")]$Strategy.y, real[Type.Effect.Cost %in% c("Reduction", "No reduction")]$Num.it.y)
table(synth[Type.Effect.Cost %in% c("Reduction", "No reduction")]$Strategy.y, synth[Type.Effect.Cost %in% c("Reduction", "No reduction")]$Num.it.y)