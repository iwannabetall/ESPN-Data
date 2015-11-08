setwd("~/Documents/Python/ESPN/Processed-PBP")
listcsv <- dir(pattern = "*.csv") # creates the list of all the csv files in the directory
#duke = read.csv(file = "Duke.csv", sep = '\t')
#WI = read.csv(file = "Wisconsin.csv", sep = '\t')
#pbp = read.csv(file = "UNC.csv")
Sec_Elapsed = function(pbp){
  seconds_elapsed = 1200 - pbp["sec_remaining"]
  ot = which(pbp["half"] > 2)
  seconds_elapsed[ot,] = 5*60 - pbp[ot, "sec_remaining"]
  seconds_elapsed[seconds_elapsed == 0] = 0.1
  return(seconds_elapsed)
}
#which(is.na(as.numeric(as.character(pbp["sec_remaining"]))))
POSS_H.R_Split = function(pbp,team,half,homegame, elapsed_group){
  #finds total possessions per time group
  ##team is 1 if it's my team; 0 if it's opponent
  #half is 1, 2, 4+ if OT
  whichhalf = which(pbp["half"] == half)
  myteam = which(pbp["my_team"] == team)
  home = which(pbp["home_game"] == homegame)
  index = intersect(intersect(myteam, whichhalf), home)
  pace = aggregate(pbp[index,"possession"] ~ elapsed_group[index], FUN = "sum")
  return(pace)
}
Margin = function(pbp){
  #margin relative to team of interest
  margin = vector(mode="numeric", length=dim(pbp)[1])
  for (i in 1:length(margin)){
    if(pbp[i,"home_game"] == 1){
      margin[i] = pbp[i,"home_score"] - pbp[i,"away_score"]
    }
    else if (pbp[i,"home_game"] == 0){
      margin[i] = pbp[i,"away_score"] - pbp[i,"home_score"] 
    }
  }
  return(margin)
}
EFF_Split = function(pbp,team,half,homegame,elapsed_group){
  #finds total turnovers per time group
  ##team is 1 if it's my team; 0 if it's opponent
  #half is 1, 2, 4+ if OT
  #home = 1 if it's home game for team of interest
  whichhalf = which(pbp["half"] == half)
  myteam = which(pbp["my_team"] == team)
  home = which(pbp["home_game"] == homegame)
  index = intersect(intersect(myteam, whichhalf), home)
  
  #Points
  Total = aggregate(points_scored[index] ~ elapsed_group[index], FUN = "sum")
  poss = POSS_H.R_Split(pbp,team,half,homegame,elapsed_group)[,2]
  Eff = Total[,2]/poss
  
  #overall = sum(Total[,2] + Total2[,2])/sum(poss + poss2)
  Eff_Stats = list("Eff" = Eff, "Total" = Total, "poss" = poss)
  return(Eff_Stats)
}
EFF = function(pbp,team,elapsed_group){
  #pbp,team,homegame, elapsed_group
  EFF_H1Home = EFF_Split(pbp,team,1,1,elapsed_group)  # $Total, $Rate, $poss
  EFF_H2Home = EFF_Split(pbp,team,2,1,elapsed_group)  # $Total, $Rate, $poss
  EFF_H1Road = EFF_Split(pbp,team,1,0,elapsed_group)  # $Total, $Rate, $poss
  EFF_H2Road = EFF_Split(pbp,team,2,0,elapsed_group)  # $Total, $Rate, $poss
  
  #pbp,team,half,homegame, elapsed_group
  EFF_H1 = (EFF_H1Home$Total[,2] + EFF_H1Road$Total[,2])/(EFF_H1Home$poss + EFF_H1Road$poss)   #first half home and road
  EFF_H2 = (EFF_H2Home$Total[,2] + EFF_H2Road$Total[,2])/(EFF_H2Home$poss + EFF_H2Road$poss)  #2nd half home and road
  Road_rate = (EFF_H1Road$Total[,2] + EFF_H2Road$Total[,2])/(EFF_H1Road$poss + EFF_H2Road$poss)
  Road_overall = sum(EFF_H1Road$Total[,2] + EFF_H2Road$Total[,2])/sum(EFF_H1Road$poss + EFF_H2Road$poss)
  Home_rate = (EFF_H1Home$Total[,2] + EFF_H2Home$Total[,2])/(EFF_H1Home$poss + EFF_H2Home$poss)
  Home_overall = sum(EFF_H1Home$Total[,2] + EFF_H2Home$Total[,2])/sum(EFF_H1Home$poss + EFF_H2Home$poss)
  Overall_by_pd = (EFF_H1Road$Total[,2] + EFF_H2Road$Total[,2] + EFF_H1Home$Total[,2] + EFF_H2Home$Total[,2])/(EFF_H1Road$poss + EFF_H2Road$poss + EFF_H1Home$poss + EFF_H2Home$poss)
  Overall = sum(EFF_H1Road$Total[,2] + EFF_H2Road$Total[,2] + EFF_H1Home$Total[,2] + EFF_H2Home$Total[,2])/sum(EFF_H1Road$poss + EFF_H2Road$poss + EFF_H1Home$poss + EFF_H2Home$poss)
  
  result = list("Overall_by_pd" = Overall_by_pd, "EFF_H1" = EFF_H1, "EFF_H2" = EFF_H2,"Overall" = Overall,"EFF_H1Road" = EFF_H1Road$Eff,"EFF_H2Road" = EFF_H2Road$Eff,"Road_rate" = Road_rate, "Road_overall" = Road_overall,"EFF_H1Home" = EFF_H1Home$Eff,"EFF_H2Home" = EFF_H2Home$Eff,"Home_rate" = Home_rate, "Home_overall" = Home_overall)
  return(result)
}
NET_EFF = function(OFF_EFF_STATS, DEF_EFF_STATS){
  Overall_by_pd = OFF_EFF_STATS$Overall_by_pd - DEF_EFF_STATS$Overall_by_pd
  NET_H1 = OFF_EFF_STATS$EFF_H1 - DEF_EFF_STATS$EFF_H1
  NET_H2 = OFF_EFF_STATS$EFF_H2 - DEF_EFF_STATS$EFF_H2
  Overall = OFF_EFF_STATS$Overall - DEF_EFF_STATS$Overall
  NET_H1Road = OFF_EFF_STATS$EFF_H1Road - DEF_EFF_STATS$EFF_H1Road
  NET_H2Road = OFF_EFF_STATS$EFF_H2Road - DEF_EFF_STATS$EFF_H2Road
  Road_rate = OFF_EFF_STATS$Road_rate - DEF_EFF_STATS$Road_rate
  Road_overall = OFF_EFF_STATS$Road_overall - DEF_EFF_STATS$Road_overall
  NET_H1Home = OFF_EFF_STATS$EFF_H1Home - DEF_EFF_STATS$EFF_H1Home
  NET_H2Home = OFF_EFF_STATS$EFF_H2Home - DEF_EFF_STATS$EFF_H2Home
  Home_rate = OFF_EFF_STATS$Home_rate - DEF_EFF_STATS$Home_rate
  Home_overall = OFF_EFF_STATS$Home_overall - DEF_EFF_STATS$Home_overall
  result = list("Overall_by_pd" = Overall_by_pd, "NET_H1" = NET_H1, "NET_H2" = NET_H2,"Overall" = Overall,"NET_H1Road" = NET_H1Road,"NET_H2Road" = NET_H2Road,"Road_rate" = Road_rate, "Road_overall" = Road_overall,"NET_H1Home" = NET_H1Home,"NET_H2Home" = NET_H2Home,"Home_rate" = Home_rate, "Home_overall" = Home_overall)
  return(result)
}
##off reb by half and home/road
Off_Reb_Split = function(pbp,team,half,homegame,elapsed_group){
  ##rebounding opps 
  whichhalf = which(pbp["half"] == half)
  myteam = which(pbp["my_team"] == team)
  home = which(pbp["home_game"] == homegame)
  index = intersect(intersect(myteam, whichhalf), home)
  totalGP = GP - awayGP*homegame - homeGP*(1-homegame)  #GP on road or home 
  
  mFGA = pbp[, "FGA"] - pbp[,"made_FGA"]  #missed FGAs
  mFGA_index = which(mFGA == 1)
  mFTA = intersect(which(points_scored == 0),which(pbp[,"FTA_RebOpp"] == 1))  #missed FTA that could be rebounded
  reb_opp = c(mFGA, mFTA)
  reb_opps = aggregate(reb_opp[index] ~ elapsed_group[index], FUN = 'sum')  #first half home game reb opps 
  poss = POSS_H.R_Split(pbp,team,1,homegame,elapsed_group)[,2]  #TOTAL possessions per X min for team of interest in 1st half of home game
  reb_opp_per_poss = reb_opps[,2]/(poss/totalGP)  ##reb opps/poss per game
  Total = aggregate(pbp[index,"off_reb"] ~ elapsed_group[index], FUN = 'sum')  ##total OREB
  OREB_Poss = Total[,2]/(poss/totalGP)   #OREB per possession-game
  OREB_RATE_PER_OPP = (Total[,2]/(poss/totalGP))/(reb_opp_per_poss)  #total off reb in season per reb opp per poss/game
  OREB_RATE_PER_OPP = Total[,2]/reb_opps[,2]
  results = list("OREB_RATE_PER_OPP" = OREB_RATE_PER_OPP, "poss" = poss, "Total" = Total, "Reb_Opps" = reb_opps)
  return(results)
}
##summary of Off rebounding stats by half and home/road, home/road overall
Off_Reb = function(pbp,team,elapsed_group){
  #finds total turnovers per time group
  ##off reb % -- percentage of eveyr missed shot and by possession 
  ##team is 1 if it's my team; 0 if it's opponent
  #half is 1, 2, 4+ if OT
  #home = 1 if it's home game for team of interest
  ## 112 + 111 + 61 + 63 = 347 OREB for ZONA; 
  ##rebounding opps 
  H1_home_rate = Off_Reb_Split(pbp,team,1,1,elapsed_group)$OREB_RATE_PER_OPP
  H2_home_rate = Off_Reb_Split(pbp,team,2,1,elapsed_group)$OREB_RATE_PER_OPP
  H1_road_rate = Off_Reb_Split(pbp,team,1,0,elapsed_group)$OREB_RATE_PER_OPP
  H2_road_rate = Off_Reb_Split(pbp,team,2,0,elapsed_group)$OREB_RATE_PER_OPP
  
  H1_home = Off_Reb_Split(pbp,team,1,1,elapsed_group)
  H2_home = Off_Reb_Split(pbp,team,2,1,elapsed_group)
  H1_road = Off_Reb_Split(pbp,team,1,0,elapsed_group)
  H2_road = Off_Reb_Split(pbp,team,2,0,elapsed_group)
  
  #by half
  total_H1_OREB_opps = H1_road$Reb_Opps[,2] + H1_home$Reb_Opps[,2]
  total_H2_OREB_opps = H2_home$Reb_Opps[,2] + H2_road$Reb_Opps[,2]
  H1_poss_total = H1_road$poss + H1_home$poss
  H2_poss_total = H2_road$poss + H2_home$poss
  H1_OREB_per_opp_Rate =total_H1_OREB_opps/H1_poss_total
  H2_OREB_per_opp_Rate =total_H2_OREB_opps/H2_poss_total
  
  #by home/road
  total_road_OREB_opps = sum(H1_road$Reb_Opps[,2] + H2_road$Reb_Opps[,2])
  total_home_OREB_opps = sum(H1_home$Reb_Opps[,2] + H2_home$Reb_Opps[,2])
  road_OREB_total = sum(H1_road$Total[,2] + H2_road$Total[,2])
  home_OREB_total = sum(H1_home$Total[,2] + H2_home$Total[,2])
  road_poss_total = sum(H1_road$poss + H2_road$poss)
  home_poss_total = sum(H1_home$poss + H2_home$poss)
  
  road_overall_poss = road_OREB_total/road_poss_total
  home_overall_poss = home_OREB_total/home_poss_total
  road_overall_perOREBopp = road_OREB_total/total_road_OREB_opps
  home_overall_perOREBopp = home_OREB_total/total_home_OREB_opps
  overall = (road_OREB_total + home_OREB_total)/(road_poss_total + home_poss_total)
  OReb_Stats = list("H1_OREB_per_opp_Rate" = H1_OREB_per_opp_Rate,"H2_OREB_per_opp_Rate" = H2_OREB_per_opp_Rate,"H1_home_rate" = H1_home_rate, "H2_home_rate" = H2_home_rate, "H1_road_rate" = H1_road_rate, "H2_road_rate" = H2_road_rate,"home_perOREBopp_rate" = home_overall_perOREBopp,"road_perOREBopp_rate" = road_overall_perOREBopp, "road_overall_poss" = road_overall_poss,"home_overall_poss" = home_overall_poss , "Overall" = overall)
  return(OReb_Stats)
}
#TURNOVERS
TO_rate = function(pbp,team,half,homegame,elapsed_group){
  #finds total turnovers per time group
  ##team is 1 if it's my team; 0 if it's opponent
  #half is 1, 2, 4+ if OT
  #home = 1 if it's home game for team of interest
  whichhalf = which(pbp["half"] == half)
  myteam = which(pbp["my_team"] == team)
  home = which(pbp["home_game"] == homegame)
  index = intersect(intersect(myteam, whichhalf), home)
  
  #TO
  Total = aggregate(pbp[index,"turnover"] ~ elapsed_group[index], FUN = 'sum')
  poss = POSS_H.R_Split(pbp,team,half,homegame,elapsed_group)[,2]
  Rate = Total[,2]/poss
  
  #overall = sum(Total[,2] + Total2[,2])/sum(poss + poss2)
  TO_Stats = list("Total" = Total,"Rate" = Rate, "poss" = poss)
  return(TO_Stats)
}
TO_Stats = function(pbp,team,elapsed_group){  
  ## 
  #pbp,team,homegame, elapsed_group
  TO_H1Home = TO_rate(pbp,team,1,1,elapsed_group)  # $Total, $Rate, $poss
  TO_H2Home = TO_rate(pbp,team,2,1,elapsed_group)  # $Total, $Rate, $poss
  TO_H1Road = TO_rate(pbp,team,1,0,elapsed_group)  # $Total, $Rate, $poss
  TO_H2Road = TO_rate(pbp,team,2,0,elapsed_group)  # $Total, $Rate, $poss
  #pbp,team,half,homegame, elapsed_group
  #H1Poss = POSS_H.R_Split(pbp,team,1,1,elapsed_group)[,2] + POSS_H.R_Split(pbp,team,1,0,elapsed_group)[,2]   #home poss
  #H2Poss = POSS_H.R_Split(pbp,team,2,1,elapsed_group)[,2] + POSS_H.R_Split(pbp,team,2,0,elapsed_group)[,2]   #home poss
  TO_H1 = (TO_H1Home$Total[,2] + TO_H1Road$Total[,2])/(TO_H1Home$poss + TO_H1Road$poss)   #first half home and road
  TO_H2 = (TO_H2Home$Total[,2] + TO_H2Road$Total[,2])/(TO_H2Home$poss + TO_H2Road$poss)  #2nd half home and road
  Road_rate = (TO_H1Road$Total[,2] + TO_H2Road$Total[,2])/(TO_H1Road$poss + TO_H2Road$poss)
  Road_overall = sum(TO_H1Road$Total[,2] + TO_H2Road$Total[,2])/sum(TO_H1Road$poss + TO_H2Road$poss)
  Home_rate = (TO_H1Home$Total[,2] + TO_H2Home$Total[,2])/(TO_H1Home$poss + TO_H2Home$poss)
  Home_overall = sum(TO_H1Home$Total[,2] + TO_H2Home$Total[,2])/sum(TO_H1Home$poss + TO_H2Home$poss)
  Overall_by_pd = (TO_H1Road$Total[,2] + TO_H2Road$Total[,2] + TO_H1Home$Total[,2] + TO_H2Home$Total[,2])/(TO_H1Road$poss + TO_H2Road$poss + TO_H1Home$poss + TO_H2Home$poss)
  Overall = sum(TO_H1Road$Total[,2] + TO_H2Road$Total[,2] + TO_H1Home$Total[,2] + TO_H2Home$Total[,2])/sum(TO_H1Road$poss + TO_H2Road$poss + TO_H1Home$poss + TO_H2Home$poss)
  
  result = list("Overall_by_pd" = Overall_by_pd, "TO_H1" = TO_H1, "TO_H2" = TO_H2,"Overall" = Overall,"TO_H1Road" = TO_H1Road$Rate,"TO_H2Road" = TO_H2Road$Rate,"Road_rate" = Road_rate, "Road_overall" = Road_overall,"TO_H1Home" = TO_H1Home$Rate,"TO_H2Home" = TO_H2Home$Rate,"Home_rate" = Home_rate, "Home_overall" = Home_overall)
  return(result)
}
###FG%
FG_P_SPLIT = function(pbp,team,half,homegame,elapsed_group){
  #finds total turnovers per time group
  ##team is 1 if it's my team; 0 if it's opponent
  #half is 1, 2, 4+ if OT
  #home = 1 if it's home game for team of interest
  whichhalf = which(pbp["half"] == half)
  myteam = which(pbp["my_team"] == team)
  home = which(pbp["home_game"] == homegame)
  index = intersect(intersect(myteam, whichhalf), home)
  
  #FGA and makes
  Total = aggregate(pbp[index,"FGA"] ~ elapsed_group[index], FUN = 'sum')
  TotalMakes = aggregate(pbp[index,"made_FGA"] ~ elapsed_group[index], FUN = 'sum')
  #poss = POSS_H.R_Split(pbp,team,half,homegame,elapsed_group)[,2]
  percent = TotalMakes[,2]/Total[,2]
  
  #overall = sum(Total[,2] + Total2[,2])/sum(poss + poss2)
  FG_P_Stats = list("TotalFGA" = Total[,2],"TotalMakes" = TotalMakes[,2], "FG_P" = percent)
  return(FG_P_Stats)
}
FG_Shooting_Stats = function(pbp,team,elapsed_group){  
  ## 
  #pbp,team,homegame, elapsed_group
  FG_P_H1Home = FG_P_SPLIT(pbp,team,1,1,elapsed_group)  # $TotalFGA, $TotalMakes, $FG_P
  FG_P_H2Home = FG_P_SPLIT(pbp,team,2,1,elapsed_group)  # $TotalFGA, $TotalMakes, $FG_P
  FG_P_H1Road = FG_P_SPLIT(pbp,team,1,0,elapsed_group)  # $TotalFGA, $TotalMakes, $FG_P
  FG_P_H2Road = FG_P_SPLIT(pbp,team,2,0,elapsed_group)  # $TotalFGA, $TotalMakes, $FG_P
  
  #pbp,team,half,homegame, elapsed_group
  FG_P_H1 = (FG_P_H1Home$TotalMakes + FG_P_H1Road$TotalMakes)/(FG_P_H1Home$TotalFGA + FG_P_H1Road$TotalFGA)  #first half home and road
  FG_P_H2 = (FG_P_H2Home$TotalMakes + FG_P_H2Road$TotalMakes)/(FG_P_H2Home$TotalFGA + FG_P_H2Road$TotalFGA) #2nd half home and road
  Road_rate = (FG_P_H1Road$TotalMakes + FG_P_H2Road$TotalMakes)/(FG_P_H1Road$TotalFGA + FG_P_H2Road$TotalFGA)
  Road_overall = sum(FG_P_H1Road$TotalMakes + FG_P_H2Road$TotalMakes)/sum(FG_P_H1Road$TotalFGA + FG_P_H2Road$TotalFGA)
  Home_rate = (FG_P_H1Home$TotalMakes + FG_P_H2Home$TotalMakes)/(FG_P_H1Home$TotalFGA + FG_P_H2Home$TotalFGA)
  Home_overall = sum(FG_P_H1Home$TotalMakes + FG_P_H2Home$TotalMakes)/sum(FG_P_H1Home$TotalFGA + FG_P_H2Home$TotalFGA)
  Overall_by_pd = (FG_P_H1Road$TotalMakes + FG_P_H2Road$TotalMakes + FG_P_H1Home$TotalMakes + FG_P_H2Home$TotalMakes)/(FG_P_H1Road$TotalFGA + FG_P_H2Road$TotalFGA + FG_P_H1Home$TotalFGA + FG_P_H2Home$TotalFGA)
  Overall = sum(FG_P_H1Road$TotalMakes + FG_P_H2Road$TotalMakes + FG_P_H1Home$TotalMakes + FG_P_H2Home$TotalMakes)/sum(FG_P_H1Road$TotalFGA + FG_P_H2Road$TotalFGA + FG_P_H1Home$TotalFGA + FG_P_H2Home$TotalFGA)
  
  result = list("Overall_by_pd" = Overall_by_pd, "FG_P_H1" = FG_P_H1, "FG_P_H2" = FG_P_H2,"FG_P_H1Road" = FG_P_H1Road$FG_P,"FG_P_H2Road" = FG_P_H2Road$FG_P ,"Road_rate" = Road_rate, "Road_overall" = Road_overall,"FG_P_H1Home" = FG_P_H1Home$FG_P, "FG_P_H2Home" = FG_P_H2Home$FG_P, "Home_rate" = Home_rate, "Home_overall" = Home_overall,"Overall" = Overall)
  return(result)
}
##fouls committed -->  my team = 1, foul = 1
##fouls drawn my team = 0, foul = 1
Foul_SPLIT = function(pbp,team,half,homegame,elapsed_group){
  #finds total turnovers per time group
  ##team is 1 if it's my team; 0 if it's opponent
  #half is 1, 2, 4+ if OT
  #home = 1 if it's home game for team of interest
  whichhalf = which(pbp["half"] == half)
  myteam = which(pbp["my_team"] == team)
  home = which(pbp["home_game"] == homegame)
  index = intersect(intersect(myteam, whichhalf), home)
  
  #fouls in first half
  Total = aggregate(pbp[index,"foul"] ~ elapsed_group[index], FUN = 'sum')
  poss = POSS_H.R_Split(pbp,team,half,homegame,elapsed_group)[,2]
  Rate = Total[,2]/poss
  
  Stats = list("Total" = Total,"Rate" = Rate, "poss" = poss)
  return(Stats)
}
Fouls_Stats = function(pbp,team,elapsed_group){
  #pbp,team,homegame, elapsed_group
  Foul_H1Home = Foul_SPLIT(pbp,team,1,1,elapsed_group)  # $Total, $Total, $Foul
  Foul_H2Home = Foul_SPLIT(pbp,team,2,1,elapsed_group)  # $Total, $Total, $Foul
  Foul_H1Road = Foul_SPLIT(pbp,team,1,0,elapsed_group)  # $Total, $Total, $Foul
  Foul_H2Road = Foul_SPLIT(pbp,team,2,0,elapsed_group)  # $Total, $Total, $Foul
  
  #pbp,team,half,homegame, elapsed_group
  Foul_H1 = (Foul_H1Home$Total[,2] + Foul_H1Road$Total[,2])/(Foul_H1Home$poss + Foul_H1Road$poss)   #first half home and road
  Foul_H2 = (Foul_H2Home$Total[,2] + Foul_H2Road$Total[,2])/(Foul_H2Home$poss + Foul_H2Road$poss)  #2nd half home and road
  Road_rate = (Foul_H1Road$Total[,2] + Foul_H2Road$Total[,2])/(Foul_H1Road$poss + Foul_H2Road$poss)
  Road_overall = sum(Foul_H1Road$Total[,2] + Foul_H2Road$Total[,2])/sum(Foul_H1Road$poss + Foul_H2Road$poss)
  Home_rate = (Foul_H1Home$Total[,2] + Foul_H2Home$Total[,2])/(Foul_H1Home$poss + Foul_H2Home$poss)
  Home_overall = sum(Foul_H1Home$Total[,2] + Foul_H2Home$Total[,2])/sum(Foul_H1Home$poss + Foul_H2Home$poss)
  Overall_by_pd = (Foul_H1Road$Total[,2] + Foul_H2Road$Total[,2] + Foul_H1Home$Total[,2] + Foul_H2Home$Total[,2])/(Foul_H1Road$poss + Foul_H2Road$poss + Foul_H1Home$poss + Foul_H2Home$poss)
  Overall = sum(Foul_H1Road$Total[,2] + Foul_H2Road$Total[,2] + Foul_H1Home$Total[,2] + Foul_H2Home$Total[,2])/sum(Foul_H1Road$poss + Foul_H2Road$poss + Foul_H1Home$poss + Foul_H2Home$poss)
  
  result = list("Overall_by_pd" = Overall_by_pd, "Foul_H1" = Foul_H1, "Foul_H2" = Foul_H2,"Foul_H1Road" = Foul_H1Road$Rate,"Foul_H2Road" = Foul_H2Road$Rate,"Road_rate" = Road_rate, "Road_overall" = Road_overall,"Foul_H1Home" = Foul_H1Home$Rate, "Foul_H2Home" = Foul_H2Home$Rate, "Home_rate" = Home_rate, "Home_overall" = Home_overall,"Overall" = Overall)
  return(result)
}
STATS_BY_TEAM = list()  
STATS = vector(mode="list", length=9)
names(STATS) = c("OFF_EFF_STATS","DEF_EFF_STATS","NET_EFF_STATS","OREB_STATS","TOs","FGShooting","FGShootingDef","Fouls","Fouls_Drawn")
for(i in 1:length(listcsv)) {
  pbp = read.csv(file = listcsv[i], sep = '\t')
  teamname = strsplit(listcsv[i],".csv")
  seconds_elapsed = Sec_Elapsed(pbp)
  margin = Margin(pbp)
  #poss = which(pbp["possession"] == 1)
  games = unique(pbp[,"Game_id"])
  
  GP = length(unique(pbp[,"Game_id"]))
  homeGP = length(unique(pbp[pbp["HomeTeam"] == teamname,"Game_id"]))
  awayGP = GP - homeGP
  
  points_scored = pbp[,"home_points_scored"] + pbp[,"away_points_scored"]
  elapsed_group = cut(seconds_elapsed[,],seq(from = 0, to = 1200, by = M*60))
  T_group = unique(elapsed_group)
  
  OFF_EFF_STATS = EFF(pbp,1,elapsed_group)
  DEF_EFF_STATS = EFF(pbp,0,elapsed_group)
  NET_EFF_STATS = NET_EFF(OFF_EFF_STATS, DEF_EFF_STATS)
  OREB_STATS = Off_Reb(pbp,1,elapsed_group)
  TOs = TO_Stats(pbp,1,elapsed_group)
  FGShooting = FG_Shooting_Stats(pbp,1,elapsed_group)
  FGShootingDef = FG_Shooting_Stats(pbp,0,elapsed_group)
  Fouls = Fouls_Stats(pbp,1,elapsed_group)  #pbp,team,homegame,elapsed_group
  Fouls_Drawn = Fouls_Stats(pbp,0,elapsed_group)
  #categories = c("OFF_EFF_STATS","DEF_EFF_STATS","NET_EFF_STATS","OREB_STATS","TOs","FGShooting","FGShootingDef","Fouls","Fouls_Drawn")
  #vars = noquote(categories)
#   for(j in 1:length(categories)){
#     print(vars[j])
#     STATS[[categories[j]]] = vars[j]
#   }
  STATS[["OFF_EFF_STATS"]] = OFF_EFF_STATS
  STATS[["DEF_EFF_STATS"]] = DEF_EFF_STATS
  STATS[["NET_EFF_STATS"]] = NET_EFF_STATS
  STATS[["OREB_STATS"]] = OREB_STATS
  STATS[["TOs"]] = TOs
  STATS[["FGShooting"]] = FGShooting
  STATS[["FGShootingDef"]] = FGShootingDef
  STATS[["Fouls"]] = Fouls
  STATS[["Fouls_Drawn"]] = Fouls_Drawn  
  STATS_BY_TEAM[[i]] = STATS
}

S = append(STATS)
S2 = list(STATS,STATS2)
S2[["Fouls"]]

STATS_BY_GAME = list()
###FOR EACH INDIVIDUAL GAME 
for(i in 1:length(listcsv)) {
  PBP = read.csv(file = listcsv[i], sep = '\t')
  teamname = strsplit(listcsv[i],".csv")
  seconds_elapsed = Sec_Elapsed(PBP)
  margin = Margin(PBP)
  #poss = which(pbp["possession"] == 1)
  games = unique(PBP[,"Game_id"])
  
  GP = length(unique(PBP[,"Game_id"]))
  homeGP = length(unique(PBP[PBP["HomeTeam"] == teamname,"Game_id"]))
  awayGP = GP - homeGP
  
  points_scored = PBP[,"home_points_scored"] + PBP[,"away_points_scored"]
  elapsed_group = cut(seconds_elapsed[,],seq(from = 0, to = 1200, by = M*60))
  T_group = unique(elapsed_group)
  print(teamname)
  for(k in 1:length(games)){
    print(games[k])
    pbpindex = which(PBP[,"Game_id"] == games[k])
    pbp = PBP[pbpindex,]
    OFF_EFF_STATS = EFF(pbp,1,elapsed_group)
    DEF_EFF_STATS = EFF(pbp,0,elapsed_group)
    NET_EFF_STATS = NET_EFF(OFF_EFF_STATS, DEF_EFF_STATS)
    OREB_STATS = Off_Reb(pbp,1,elapsed_group)
    TOs = TO_Stats(pbp,1,elapsed_group)
    FGShooting = FG_Shooting_Stats(pbp,1,elapsed_group)
    FGShootingDef = FG_Shooting_Stats(pbp,0,elapsed_group)
    Fouls = Fouls_Stats(pbp,1,elapsed_group)  #pbp,team,homegame,elapsed_group
    Fouls_Drawn = Fouls_Stats(pbp,0,elapsed_group)
    STATS = vector(mode="list", length=9)
    names(STATS) = c("OFF_EFF_STATS","DEF_EFF_STATS","NET_EFF_STATS","OREB_STATS","TOs","FGShooting","FGShootingDef","Fouls","Fouls_Drawn")
    STATS_BY_GAME[[i]] = STATS
    }
}
 #pbp,team,homegame,elapsed_group

#######################################################################################################################################
#######################################################################################################################################

#OFF REB RATE?

##seconds elapsed 


aggregate(pbp[,"possession"] ~ pbp[,"Game_id"], FUN = 'sum')
first_half_margin = aggregate(margin[firsthalf] ~ timegroup[firsthalf], FUN = "mean")
second_half_margin = aggregate(margin[secondhalf] ~ timegroup[secondhalf], FUN = "mean")

}

##########################################
#############home vs. road  #############
##########################################

home = which(pbp["home_game"] == 1)
road = which(pbp["home_game"] == 0)

H1poss_home = intersect(intersect(myteam, firsthalf), home)  ## possessions by team of choice in 1st half
H2poss_home = intersect(intersect(myteam, secondhalf), home)  ## possessions by team of choice in 2nd half
H1poss_road = intersect(intersect(myteam, firsthalf), road)  ## possessions by team of choice in 1st half
H2poss_road = intersect(intersect(myteam, secondhalf), road)  ## possessions by team of choice in 2nd half

##opponent points when team is on the road (opponent's offense)
oppH1poss_home = intersect(intersect(opp, firsthalf), home)  ## possessions by opponent in 1st half in home game (for team of choice)
oppH2poss_home = intersect(intersect(opp, secondhalf), home)  ## possessions by opponent in 2nd half in home game (for team of choice)
oppH1poss_road = intersect(intersect(opp, firsthalf), road)  ## possessions by opponent in 1st half in road game (for team of choice)
oppH2poss_road = intersect(intersect(opp, secondhalf), road)  ## possessions by opponent in 1st half in road game (for team of choice)

##possessions/pace 
    ##pace comparison -- possessions for myteam 
H1PaceT4 = aggregate(pbp[H1poss_home,"possession"] ~ elapsedT4[H1poss_home], FUN = "sum")   #poss/game in home games 
H2PaceT4 = aggregate(pbp[H2poss_home,"possession"] ~ elapsedT4[H2poss_home], FUN = "sum")
oppH1PaceT4 = aggregate(pbp[oppH1poss_home,"possession"] ~ elapsedT4[oppH1poss_home], FUN = "sum")   #opponent poss/game in home games
oppH2PaceT4 = aggregate(pbp[oppH2poss_home,"possession"] ~ elapsedT4[oppH2poss_home], FUN = "sum")

##road 
rH1PaceT4 = aggregate(pbp[H1poss_road,"possession"] ~ elapsedT4[H1poss_road], FUN = "sum")   # PPP on the road 
rH2PaceT4 = aggregate(pbp[H2poss_road,"possession"] ~ elapsedT4[H2poss_road], FUN = "sum")
roppH1PaceT4 = aggregate(pbp[oppH1poss_road,"possession"] ~ elapsedT4[oppH1poss_road], FUN = "sum")   ##opp poss/game
roppH2PaceT4 = aggregate(pbp[oppH2poss_road,"possession"] ~ elapsedT4[oppH2poss_road], FUN = "sum")

    ##points scored 
H1PTS = aggregate(points_scored[H1poss_home] ~ elapsedT4[H1poss_home], FUN = 'sum')
H2PTS = aggregate(points_scored[H2poss_home] ~ elapsedT4[H2poss_home], FUN = 'sum')
rH1PTS = aggregate(points_scored[H1poss_road] ~ elapsedT4[H1poss_road], FUN = 'sum')   #road off eff
rH2PTS = aggregate(points_scored[H2poss_road] ~ elapsedT4[H2poss_road], FUN = 'sum')

oppH1PTS = aggregate(points_scored[oppH1poss_home] ~ elapsedT4[oppH1poss_home], FUN = 'sum')  ## def efficiency on road 
oppH2PTS = aggregate(points_scored[oppH2poss_home] ~ elapsedT4[oppH2poss_home], FUN = 'sum')
roppH1PTS = aggregate(points_scored[oppH1poss_road] ~ elapsedT4[oppH1poss_road], FUN = 'sum')  ##def efficiency at home 
roppH2PTS = aggregate(points_scored[oppH2poss_road] ~ elapsedT4[oppH2poss_road], FUN = 'sum')

##efficiency per poss 
H1PPP = cbind(H1PTS[,1], H1PTS[,2]/H1PaceT4[,2])  #home PPP
H2PPP = cbind(H2PTS[,1], H2PTS[,2]/H2PaceT4[,2])  # home PPP, 2nd half
rH1PPP = cbind(H1PTS[,1], rH1PTS[,2]/rH1PaceT4[,2])  #road PPP
rH2PPP = cbind(H2PTS[,1], rH2PTS[,2]/rH2PaceT4[,2])   #road PPP, 2nd half
      
    #defensive efficiency
oppH1PPP = cbind(oppH1PTS[,1], oppH1PTS[,2]/oppH1PaceT4[,2])  #defensive PPP in home games
oppH2PPP = cbind(oppH2PTS[,1], oppH2PTS[,2]/oppH2PaceT4[,2])
roppH1PPP = cbind(oppH1PTS[,1], roppH1PTS[,2]/roppH1PaceT4[,2])  #defensive PPP in road games
roppH2PPP = cbind(oppH2PTS[,1], roppH2PTS[,2]/roppH2PaceT4[,2])

#turnovers
H1TO = aggregate(pbp[H1poss_home,"turnover"] ~ elapsedT4[H1poss_home], FUN = 'sum')
H2TO = aggregate(pbp[H2poss_home,"turnover"] ~ elapsedT4[H2poss_home], FUN = 'sum')
rH1TO = aggregate(pbp[H1poss_road,"turnover"] ~ elapsedT4[H1poss_road], FUN = 'sum')   #road off eff
rH2TO = aggregate(pbp[H2poss_road,"turnover"] ~ elapsedT4[H2poss_road], FUN = 'sum')
turnovers_PG = sum(H1TO[,2], H2TO[,2], rH1TO[,2], rH2TO[,2])/37

###to rate
H1TO_RATE = cbind(H1TO[,1], H1TO[,2]/H1PaceT4[,2])  #home TO RATE
H2TO_RATE = cbind(H2TO[,1], H2TO[,2]/H2PaceT4[,2])  # home TO RATE, 2nd half
rH1TO_RATE = cbind(H1TO[,1], rH1TO[,2]/rH1PaceT4[,2])  #road TO RATE
rH2TO_RATE = cbind(H2TO[,1], rH2TO[,2]/rH2PaceT4[,2])   #road TO RATE, 2nd half
plot(H1TO_RATE[,2], H1PPP[,2])
points(H2TO_RATE[,2], H2PPP[,2])
points(rH1TO_RATE[,2], rH1PPP[,2])
points(rH2TO_RATE[,2], rH2PPP[,2])

fga = aggregate(pbp[myteam,"FGA"] ~ elapsedT4[myteam], FUN = "sum")
fgm = aggregate(pbp[myteam,"made_FGA"] ~ elapsedT4[myteam], FUN = "sum")


fga1 = aggregate(pbp[intersect(myteam, firsthalf),"FGA"] ~ elapsedT4[intersect(myteam, firsthalf)], FUN = "sum")
fga2 = aggregate(pbp[intersect(myteam, secondhalf),"FGA"] ~ elapsedT4[intersect(myteam, secondhalf)], FUN = "sum")
fgm1 = aggregate(pbp[intersect(myteam, firsthalf),"made_FGA"] ~ elapsedT4[intersect(myteam, firsthalf)], FUN = "sum")
fgm2 = aggregate(pbp[intersect(myteam, secondhalf),"made_FGA"] ~ elapsedT4[intersect(myteam, secondhalf)], FUN = "sum")
####****
plot(fga2[,1], fgm2[,2]/fga2[,2])  #plot FG% by time group 2nd half 
points(fga1[,1], fgm1[,2]/fga1[,2], col = 'red')  #plot FG% by minute 

##for T1

fga1 = aggregate(pbp[intersect(myteam, firsthalf),"FGA"] ~ elapsedT1[intersect(myteam, firsthalf)], FUN = "sum")
fga2 = aggregate(pbp[intersect(myteam, secondhalf),"FGA"] ~ elapsedT1[intersect(myteam, secondhalf)], FUN = "sum")
fgm1 = aggregate(pbp[intersect(myteam, firsthalf),"made_FGA"] ~ elapsedT1[intersect(myteam, firsthalf)], FUN = "sum")
fgm2 = aggregate(pbp[intersect(myteam, secondhalf),"made_FGA"] ~ elapsedT1[intersect(myteam, secondhalf)], FUN = "sum")
####****
plot(fga2[,1], fgm2[,2]/fga2[,2])  #plot FG% by time group 2nd half 
points(fga1[,1], fgm1[,2]/fga1[,2], col = 'red')  #plot FG% by minute 
######
TO = aggregate(pbp[myteam,"turnover"] ~ elapsedT4[myteam], FUN = "sum")
TO1 = aggregate(pbp[intersect(myteam, firsthalf),"turnover"] ~ elapsedT1[intersect(myteam, firsthalf)], FUN = "sum")
TO2 = aggregate(pbp[intersect(myteam, secondhalf),"turnover"] ~ elapsedT1[intersect(myteam, secondhalf)], FUN = "sum")

points(TO1[,1], TO1[,2]/37, col = 'red') #TURNOVERS/MINUTE-game 
plot(TO2[,1], TO2[,2]/37)
TwoMin = seq(0, 1200, by = 120)

fgm = aggregate(pbp[myteam,"made_FGA"] ~ elapsedT4[myteam], FUN = "sum")

plot(first_half_margin[,1],first_half_margin[,2],col = "blue")
plot(second_half_margin[,1],second_half_margin[,2], col = "red")

t2 = pbp["half" == 2,"sec_remaining"]
timegroup = cut(pbp[,"sec_remaining"],seq(from = 0, to = 1200, by = 60))
T4 = cut(pbp[,"sec_remaining"],seq(from = 0, to = 1200, by = 240))
H1_group = timegroup[pbp["half"] == 1]
H2_group = timegroup[pbp["half"] == 2]

elapsedT4 = cut(seconds_elapsed[,],seq(from = 0, to = 1200, by = 240))
elapsedT2 = cut(seconds_elapsed[,],seq(from = 0, to = 1200, by = 120))
elapsedT1 = cut(seconds_elapsed[,],seq(from = 0, to = 1200, by = 60))


firsthalf = which(pbp["half"] == 1)
secondhalf = which(pbp["half"] == 2)

myteam = which(pbp["my_team"] == 1)
opp = which(pbp["my_team"] == 0)
##pace comparison 
H1PaceT4 = aggregate(pbp[intersect(myteam, firsthalf),"possession"] ~ elapsedT4[intersect(myteam, firsthalf)], FUN = "sum")
H2PaceT4 = aggregate(pbp[intersect(myteam, secondhalf),"possession"] ~ elapsedT4[intersect(myteam, secondhalf)], FUN = "sum")
oppH1PaceT4 = aggregate(pbp[intersect(opp, firsthalf),"possession"] ~ elapsedT4[intersect(opp, firsthalf)], FUN = "sum")
oppH2PaceT4 = aggregate(pbp[intersect(opp, secondhalf),"possession"] ~ elapsedT4[intersect(opp, secondhalf)], FUN = "sum")
###
H1PTS = aggregate(points_scored[intersect(myteam, firsthalf)] ~ elapsedT4[intersect(myteam, firsthalf)], FUN = 'sum')
H2PTS = aggregate(points_scored[intersect(myteam, secondhalf)] ~ elapsedT4[intersect(myteam, secondhalf)], FUN = 'sum')
oppH1PTS = aggregate(points_scored[intersect(opp, firsthalf)] ~ elapsedT4[intersect(opp, firsthalf)], FUN = 'sum')
oppH2PTS = aggregate(points_scored[intersect(opp, secondhalf)] ~ elapsedT4[intersect(opp, secondhalf)], FUN = 'sum')

##efficiency per poss 
H1PPP = cbind(H1PTS[,1], H1PTS[,2]/H1PaceT4[,2])
H2PPP = cbind(H2PTS[,1], H2PTS[,2]/H2PaceT4[,2])
oppH1PPP = cbind(oppH1PTS[,1], oppH1PTS[,2]/oppH1PaceT4[,2])
oppH2PPP = cbind(oppH2PTS[,1], oppH2PTS[,2]/oppH2PaceT4[,2])

H1netPPP = cbind(H1PTS[,1], H1PTS[,2]/H1PaceT4[,2] - oppH1PTS[,2]/oppH1PaceT4[,2])
H2netPPP = cbind(oppH2PTS[,1], H2PTS[,2]/H2PaceT4[,2] - oppH2PTS[,2]/oppH2PaceT4[,2])

H1poss = poss(pbp,1,1,elapsed_group)
H2poss = poss(pbp,1,2,elapsed_group)
H2poss = poss(pbp,0,2,elapsed_group)
H2pts = pts(pbp,1,2,elapsed_group)


overall_off_eff = sum(points_scored[myteam])/sum(pbp[myteam,"possession"])
overall_def_eff = sum(points_scored[opp])/sum(pbp[opp,"possession"])

TO_HomeStats = TO_rate(pbp,1,1,elapsed_group)  # $Total1, $Total2, $Rate1, $Rate2, $Overall
TO_RoadStats = TO_rate(pbp,1,0,elapsed_group)  # $Total1, $Total2, $Rate1, $Rate2, $Overall
H1Poss = POSS_H.R_Split(pbp,1,1,1,elapsed_group)[,2] + POSS_H.R_Split(pbp,1,1,0,elapsed_group)[,2]   #home poss
H2Poss = POSS_H.R_Split(pbp,1,2,1,elapsed_group)[,2] + POSS_H.R_Split(pbp,1,2,0,elapsed_group)[,2]   #home poss
TO_NoSplit1 = (TO_HomeStats$Total1[,2] + TO_RoadStats$Total1[,2])/H1Poss   #first half home and road
TO_NoSplit2 = (TO_HomeStats$Total2[,2] + TO_RoadStats$Total2[,2])/H2Poss  #2nd half home and road

POSS = function(pbp,team,half,elapsed_group){
  #finds possessions per time group
  ##team is 1 if it's my team; 0 if it's opponent
  #half is 1, 2, 4+ if OT
  whichhalf = which(pbp["half"] == half)
  myteam = which(pbp["my_team"] == team)
  pace = aggregate(pbp[intersect(myteam, whichhalf),"possession"] ~ elapsed_group[intersect(myteam, whichhalf)], FUN = "sum")
  return(pace)
}

PTS = function(pbp,team,half,elapsed_group){
  #finds total points scored per time group
  ##team is 1 if it's my team; 0 if it's opponent
  #half is 1, 2, 4+ if OT
  whichhalf = which(pbp["half"] == half)
  myteam = which(pbp["my_team"] == team)
  pts = aggregate(points_scored[intersect(myteam, whichhalf)] ~ elapsed_group[intersect(myteam, whichhalf)], FUN = "sum")
  
  
  return(pts)
}
EFF = function(pbp,team,half,elapsed_group){
  poss = POSS(pbp,team,half,elapsed_group)
  pts = PTS(pbp,team,half,elapsed_group)
  eff = pts[,2]/poss[,2]
  return(eff)
}

H1_off_eff = EFF(pbp,1,1,elapsed_group)
H2_off_eff = EFF(pbp,1,2,elapsed_group)
H1_def_eff = EFF(pbp,0,1,elapsed_group)
H2_def_eff = EFF(pbp,0,2,elapsed_group)

H1Pt_Diff = PTS(pbp,1,1,elapsed_group)[,2] - PTS(pbp,0,1,elapsed_group)[,2]
H2Pt_Diff = PTS(pbp,1,2,elapsed_group)[,2] - PTS(pbp,0,2,elapsed_group)[,2]
H1_net_eff = H1_off_eff - H1_def_eff
H2_net_eff = H2_off_eff - H2_def_eff
overall_eff = Overall_EFF(pbp,1,1,elapsed_group)  # $H1, $H2, $overall 
overall_def_eff = Overall_EFF(pbp,0,1,elapsed_group)

TO_HomeStats = TO_rate(pbp,1,1,elapsed_group)  # $Total1, $Total2, $Rate1, $Rate2, $Overall
TO_RoadStats = TO_rate(pbp,1,0,elapsed_group)  # $Total1, $Total2, $Rate1, $Rate2, $Overall
H1Poss = POSS_H.R_Split(pbp,1,1,1,elapsed_group)[,2] + POSS_H.R_Split(pbp,1,1,0,elapsed_group)[,2]   #home poss
H2Poss = POSS_H.R_Split(pbp,1,2,1,elapsed_group)[,2] + POSS_H.R_Split(pbp,1,2,0,elapsed_group)[,2]   #home poss
TO_NoSplit1 = (TO_HomeStats$Total1[,2] + TO_RoadStats$Total1[,2])/H1Poss   #first half home and road
TO_NoSplit2 = (TO_HomeStats$Total2[,2] + TO_RoadStats$Total2[,2])/H2Poss  #2nd half home and road

STATS2 = vector(mode="list", length=9)
names(STATS2) = c("OFF_EFF_STATS","DEF_EFF_STATS","NET_EFF_STATS","OREB_STATS","TOs","FGShooting","FGShootingDef","Fouls","Fouls_Drawn")
STATS2[["OFF_EFF_STATS"]] = OFF_EFF_STATS
STATS2[["DEF_EFF_STATS"]] = DEF_EFF_STATS
STATS2[["NET_EFF_STATS"]] = NET_EFF_STATS
STATS2[["OREB_STATS"]] = OREB_STATS
STATS2[["TOs"]] = TOs
STATS2[["FGShooting"]] = FGShooting
STATS2[["FGShootingDef"]] = FGShootingDef
STATS2[["Fouls"]] = Fouls
STATS2[["Fouls_Drawn"]] = Fouls_Drawn
