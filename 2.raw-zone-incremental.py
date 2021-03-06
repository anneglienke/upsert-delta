# Incremental ingestion (append) to raw-zone

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql import SQLContext

if __name__ == '__main__':
    
    # Create Spark session
    spark = SparkSession \
      .builder \
      .appName("Job - Increment Raw-Zone") \
      .getOrCreate()    

    # Read delta
    delta_data = spark.read \
    .format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true")  \
    .load("titanic2.csv")

    # Create delta view
    delta_data.createOrReplaceTempView("deltaView")

    # Read raw-zone and create raw view
    raw_data = spark.read.format("parquet").load("raw-zone/")
    raw_data.createOrReplaceTempView("rawView")
   
   # Create incremented view with only new data 
    incrementedView = spark.sql(
        """SELECT * 
        FROM deltaView AS d
        WHERE d.CHANGE_TIMESTAMP > (SELECT max(CHANGE_TIMESTAMP)
                                    FROM rawView AS r)
            """)
    #incrementedView.show(truncate=False)  

    # Append incremented data to raw-zone
    incrementedView.write.mode("append").parquet("raw-zone/")

    # Stop Spark session
    spark.stop()












