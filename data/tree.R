
irrigation="C:\Users\shyam\Documents\GitHub\FIT3164\data\irrigation_table- clean binary.csv"
train.row=sample(1:nrow(irrigation),0.7*nrow(irrigation))
irri.train=irrigation[train.row,]
irii.test=irrigation[-train.row]
  
fit_tree=tree(Method~.,data=irri.train)
summary(fit_tree)
plot(fit_tree)
text(fit_tree,pretty=0)
  
##Testing the model
tpredict=predict(fit_tree,irri.test,type="class")
table(actual=irri.test,predicted=tpredict)
