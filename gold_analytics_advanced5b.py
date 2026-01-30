# Databricks notebook source
dbutils.widgets.text("catalog","")
CATALOG=dbutils.widgets.get("catalog").strip()
dbutils.widgets.text("schema","")
SCHEMA=dbutils.widgets.get("schema").strip()

# COMMAND ----------

import json

config_nb_output = dbutils.notebook.run(
    "/Workspace/Users/loganathansundaramsa@gmail.com/dataengg_inc_learning/databricks_learning/generic_project/general_conf_utils_1_2/configs_path1",
    120,{"catalog": CATALOG,"schema": SCHEMA})

config_dict = json.loads(config_nb_output)

CATALOG = config_dict["CATALOG"]
SCHEMA = config_dict["SCHEMA"]
SRC=config_dict["SRC"]
BRONZE = config_dict["BRONZE"]
SILVER = config_dict["SILVER"]
GOLD = config_dict["GOLD"]
SILVERDB = config_dict["SILVERDB"]
GOLDDB = config_dict["GOLDDB"]

# COMMAND ----------

# MAGIC %run /Workspace/Users/loganathansundaramsa@gmail.com/dataengg_inc_learning/databricks_learning/generic_project/general_conf_utils_1_2/util_functions2

# COMMAND ----------

from pyspark.sql.window import Window

df = spark.read.format("delta").load(f"{GOLD}/core_curated")
df.show()
# TOP 3 DRIVERS BY COST PER HUB
w = Window.partitionBy("origin_hub_city") \
          .orderBy(F.col("shipment_cost").desc())

top3 = df.withColumn("rank", F.dense_rank().over(w)) \
         .filter("rank <= 3")

# LEAD / LAG
lag_df = df.withColumn(
    "prev_shipment_days",
    F.lag("shipment_year").over(
        Window.partitionBy("masked_staff_name").orderBy("shipment_year")
    )
)

# CUBE AGGREGATION
cube_df = df.cube("origin_hub_city") \
    .agg(F.sum("shipment_cost").alias("total_cost"))

write_file(top3,f"{GOLD}/top3_drivers")
write_file(lag_df,f"{GOLD}/prev_shipment_days")
write_file(cube_df,f"{GOLD}/cube_costs")