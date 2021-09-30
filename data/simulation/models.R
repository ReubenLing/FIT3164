data= read.csv("sample_output.csv")
data_non_irrigating=data.frame(data[data["irrigating."]=="no",])
data_irrigating=data.frame(data[data["irrigating."]=="yes",])
#droplevels.factor(data_irrigating)
#data_irrigating=na.omit(data_irrigating)
df=subset(data_irrigating, select = -c(location,farm_name,irrigating.) )
df_1=subset(data_non_irrigating, select = -c(location,farm_name,irrigating.) )

fit_irr=lm(avg_daily_water_usage~.-num_cows,data=df_1)
summary(fit_irr)

fit_irr=lm(avg_daily_water_usage~ .,data=df)
summary(fit_irr)

