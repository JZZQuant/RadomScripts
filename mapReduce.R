#setup devtools from 
#https://www.digitalocean.com/community/tutorials/how-to-set-up-r-on-ubuntu-14-04
# also install RCurl
# download spark from sparkwebite and unzipit to the spark_home env path
library(devtools)
install_github('apache/spark@v1.6.1', subdir='R/pkg')

#load spark and ggplot
library(SparkR)
Sys.setenv(SPARK_HOME="/opt/spark")
sparkcontext <- sparkR.init("local","kippo",sparkEnvir=list(spark.executor.memory="4g"))
sqlC<-sparkRSQL.init(sparkcontext)
library(ggplot2)

#load data and extract  listed count after mapreduce
rdd<-SparkR:::textFile(sparkcontext,"file:///home/euler/projects/kippo/data/kippo.*")
filtered_rdd<-SparkR:::filterRDD(rdd,function(x){grepl("login attempt",x)})
mappedrdd<-SparkR:::map(filtered_rdd,function(x){list(gsub(" .*","",x),as.integer(grepl("succeeded",x)))})
trend<-SparkR:::collect(SparkR:::reduceByKey(mappedrdd,function(a, b) { a + b},1))
sparkR.stop()

#create  a dataframe
attacks<-unlist(lapply(trend,function(x){x[[2]]}))
date<-unlist(lapply(trend,function(x){x[[1]]}))
df<-data.frame(date,attacks)
df<-transform(df,date=as.Date(date))

#plot
ggplot(df, aes(date, attacks)) + geom_line() + xlab("") + ylab("Daily Views")
