library(tree)
library(e1071)

d = read.csv("Irrigation_table - clean binary.csv", encoding="UTF-8")
for(i in seq(2, 29)) {
  d[,i] = as.factor(d[,i])
}
attach(d)

nbayes = naiveBayes(X.U.FEFF.Method~., data=d)
