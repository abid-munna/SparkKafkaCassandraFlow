from pyspark.sql import SparkSession
from pyspark.sql.types import StructType,StructField,LongType,IntegerType,FloatType,StringType
from pyspark.sql.functions import split,from_json,col

odometrySchema = StructType([
                StructField("id",IntegerType(),False),
                StructField("posex",FloatType(),False),
                StructField("posey",FloatType(),False),
                StructField("posez",FloatType(),False),
                StructField("orientx",FloatType(),False),
                StructField("orienty",FloatType(),False),
                StructField("orientz",FloatType(),False),
                StructField("orientw",FloatType(),False)
            ])

spark = SparkSession \
    .builder \
    .appName("SSKafka") \
    .config("spark.driver.host", "localhost")\
    .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")


df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "172.18.0.4:9092") \
  .option("subscribe", "rosmsgs") \
  .option("delimeter",",") \
  .option("startingOffsets", "earliest") \
  .load() 

df.printSchema()

df1 = df.selectExpr("CAST(value AS STRING)").select(from_json(col("value"),odometrySchema).alias("data")).select("data.*")
df1.printSchema()

df1.writeStream \
  .outputMode("update") \
  .format("console") \
  .option("truncate", False) \
  .start() \
  .awaitTermination()
