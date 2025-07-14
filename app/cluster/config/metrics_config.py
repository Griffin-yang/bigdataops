# 主机级指标配置
HOST_METRICS = {
    "cpu_usage": {
        "query": "(1 - avg(rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) by (instance)) * 100",
        "description": "CPU使用率"
    },
    "memory_usage": {
        "query": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
        "description": "内存使用率"
    },
    "disk_usage": {
        "query": "max((node_filesystem_size_bytes{fstype=~\"ext.?|xfs\"}-node_filesystem_free_bytes{fstype=~\"ext.?|xfs\"}) *100/(node_filesystem_avail_bytes{fstype=~\"ext.?|xfs\"}+(node_filesystem_size_bytes{fstype=~\"ext.?|xfs\"}-node_filesystem_free_bytes{fstype=~\"ext.?|xfs\"})))by(instance)",
        "description": "磁盘使用率"
    },
    "memory_total": {
        "query": "node_memory_MemTotal_bytes",
        "description": "总内存"
    },
    "cpu_cores": {
        "query": "count(node_cpu_seconds_total{mode='system'}) by (instance)",
        "description": "CPU核数"
    },
    "load_5m": {
        "query": "node_load5",
        "description": "5分钟负载"
    },
    "uptime_days": {
        "query": "sum(time() - node_boot_time_seconds)by(instance)/86400",
        "description": "系统运行天数"
    },
    "disk_read_rate": {
        "query": "max(rate(node_disk_read_bytes_total[5m])) by (instance)",
        "description": "磁盘读取速率"
    },
    "disk_write_rate": {
        "query": "max(rate(node_disk_written_bytes_total[5m])) by (instance)",
        "description": "磁盘写入速率"
    },
    "network_recv_rate": {
        "query": "max(rate(node_network_receive_bytes_total[5m])*8) by (instance)",
        "description": "网络接收速率"
    },
    "network_send_rate": {
        "query": "max(rate(node_network_transmit_bytes_total[5m])*8) by (instance)",
        "description": "网络发送速率"
    },
    "tcp_connections": {
        "query": "node_netstat_Tcp_CurrEstab",
        "description": "TCP连接数"
    },
    "disk_io_util": {
        "query": "max(rate(node_disk_io_time_seconds_total[5m])) by (instance) *100",
        "description": "磁盘IO使用率"
    }
}

# HDFS组件指标
HDFS_METRICS = {
    "namenode_status": {
        "query": "up{job=\"hdfs-namenode\"}",
        "description": "NameNode运行状态"
    },
    "namenode_heap_memory": {
        "query": "jvm_memory_bytes_used{job=\"hdfs-namenode\",area=\"heap\"}",
        "description": "NameNode堆内存使用量"
    },
    "hdfs_capacity_total": {
        "query": "hadoop_namenode_capacitytotal",
        "description": "HDFS总容量"
    },
    "hdfs_capacity_used": {
        "query": "hadoop_namenode_capacityused",
        "description": "HDFS已用容量"
    },
    "hdfs_capacity_remaining": {
        "query": "hadoop_namenode_capacityremaining",
        "description": "HDFS剩余容量"
    },
    "hdfs_blocks_total": {
        "query": "hadoop_namenode_blockstotal",
        "description": "HDFS总块数"
    },
    "datanode_status": {
        "query": "up{job=\"hdfs-datanode\"}",
        "description": "DataNode运行状态"
    },
    "datanode_capacity": {
        "query": "hadoop_datanode_capacity",
        "description": "DataNode容量"
    },
    "datanode_dfs_used": {
        "query": "hadoop_datanode_dfsused",
        "description": "DataNode DFS使用量"
    },
    "datanode_remaining": {
        "query": "hadoop_datanode_remaining",
        "description": "DataNode剩余空间"
    }
}

# YARN组件指标
YARN_METRICS = {
    "resourcemanager_status": {
        "query": "up{job=\"yarn-resourcemanager\"}",
        "description": "ResourceManager运行状态"
    },
    "yarn_active_nodes": {
        "query": "hadoop_resourcemanager_activenodes",
        "description": "YARN活跃节点数"
    },
    "yarn_memory_total": {
        "query": "hadoop_resourcemanager_totalmb",
        "description": "YARN总内存"
    },
    "yarn_memory_allocated": {
        "query": "hadoop_resourcemanager_allocatedmb",
        "description": "YARN已分配内存"
    },
    "yarn_vcores_total": {
        "query": "hadoop_resourcemanager_totalvirtualcores",
        "description": "YARN总虚拟核数"
    },
    "yarn_vcores_allocated": {
        "query": "hadoop_resourcemanager_allocatedvirtualcores",
        "description": "YARN已分配虚拟核数"
    },
    "nodemanager_status": {
        "query": "up{job=\"yarn-nodemanager\"}",
        "description": "NodeManager运行状态"
    }
}

# Spark组件指标
SPARK_METRICS = {
    "spark_master_status": {
        "query": "up{job=\"spark-master\"}",
        "description": "Spark Master运行状态"
    },
    "spark_workers_alive": {
        "query": "spark_master_aliveWorkers",
        "description": "Spark存活Worker数量"
    },
    "spark_applications_running": {
        "query": "spark_master_apps",
        "description": "Spark运行中应用数"
    },
    "spark_worker_status": {
        "query": "up{job=\"spark-worker\"}",
        "description": "Spark Worker运行状态"
    },
    "spark_worker_executors": {
        "query": "spark_worker_executors",
        "description": "Spark Worker Executor数量"
    },
    "spark_worker_memory_used": {
        "query": "spark_worker_memory_used",
        "description": "Spark Worker内存使用量"
    },
    "spark_history_server_status": {
        "query": "up{job=\"spark-history-server\"}",
        "description": "Spark History Server运行状态"
    }
}

# Hive组件指标
HIVE_METRICS = {
    "hive_metastore_status": {
        "query": "up{job=\"hive-metastore\"}",
        "description": "Hive Metastore运行状态"
    },
    "hive_metastore_connections": {
        "query": "hive_metastore_open_connections",
        "description": "Hive Metastore连接数"
    },
    "hiveserver2_status": {
        "query": "up{job=\"hiveserver2\"}",
        "description": "HiveServer2运行状态"
    },
    "hiveserver2_sessions": {
        "query": "hiveserver2_open_sessions",
        "description": "HiveServer2会话数"
    }
}

# Kafka组件指标
KAFKA_METRICS = {
    "kafka_broker_status": {
        "query": "up{job=\"kafka\"}",
        "description": "Kafka Broker运行状态"
    },
    "kafka_messages_in_rate": {
        "query": "rate(kafka_server_brokertopicmetrics_messagesin_total[5m])",
        "description": "Kafka消息输入速率"
    },
    "kafka_bytes_in_rate": {
        "query": "rate(kafka_server_brokertopicmetrics_bytesin_total[5m])",
        "description": "Kafka字节输入速率"
    },
    "kafka_bytes_out_rate": {
        "query": "rate(kafka_server_brokertopicmetrics_bytesout_total[5m])",
        "description": "Kafka字节输出速率"
    }
}

# ZooKeeper组件指标
ZOOKEEPER_METRICS = {
    "zookeeper_status": {
        "query": "up{job=\"zookeeper\"}",
        "description": "ZooKeeper运行状态"
    },
    "zookeeper_leader": {
        "query": "zk_server_state{state=\"leader\"}",
        "description": "ZooKeeper Leader状态"
    },
    "zookeeper_followers": {
        "query": "zk_server_state{state=\"follower\"}",
        "description": "ZooKeeper Follower状态"
    },
    "zookeeper_watchers": {
        "query": "zk_num_alive_connections",
        "description": "ZooKeeper监视器数量"
    }
}

# Flink组件指标
FLINK_METRICS = {
    "flink_jobmanager_status": {
        "query": "up{job=\"flink-jobmanager\"}",
        "description": "Flink JobManager运行状态"
    },
    "flink_taskmanager_status": {
        "query": "up{job=\"flink-taskmanager\"}",
        "description": "Flink TaskManager运行状态"
    },
    "flink_jobs_running": {
        "query": "flink_jobmanager_numRunningJobs",
        "description": "Flink运行中任务数"
    },
    "flink_taskslots_total": {
        "query": "flink_jobmanager_taskSlotsTotal",
        "description": "Flink总任务槽数"
    },
    "flink_taskslots_available": {
        "query": "flink_jobmanager_taskSlotsAvailable",
        "description": "Flink可用任务槽数"
    }
}

# 组合所有组件指标
ALL_COMPONENT_METRICS = {
    "hdfs": HDFS_METRICS,
    "yarn": YARN_METRICS,
    "spark": SPARK_METRICS,
    "hive": HIVE_METRICS,
    "kafka": KAFKA_METRICS,
    "zookeeper": ZOOKEEPER_METRICS,
    "flink": FLINK_METRICS
}

# 组件角色映射
COMPONENT_ROLES = {
    # HDFS角色
    "hdfs-namenode_status": "NameNode",
    "hdfs-datanode_status": "DataNode",
    "hdfs-journalnode_status": "JournalNode",
    
    # YARN角色
    "yarn-resourcemanager_status": "ResourceManager",
    "yarn-nodemanager_status": "NodeManager",
    
    # Spark角色
    "spark-spark_master_status": "Spark Master",
    "spark-spark_worker_status": "Spark Worker",
    "spark-spark_history_server_status": "Spark History Server",
    
    # Hive角色
    "hive-hive_metastore_status": "Hive Metastore",
    "hive-hiveserver2_status": "HiveServer2",
    
    # Kafka角色
    "kafka-kafka_broker_status": "Kafka Broker",
    
    # ZooKeeper角色
    "zookeeper-zookeeper_status": "ZooKeeper",
    
    # Flink角色
    "flink-flink_jobmanager_status": "Flink JobManager",
    "flink-flink_taskmanager_status": "Flink TaskManager"
}

# 端口配置
COMPONENT_PORTS = {
    "hdfs": {
        "namenode": [9870, 8020],
        "datanode": [9864, 9866],
        "journalnode": [8485, 8480]
    },
    "yarn": {
        "resourcemanager": [8088, 8030],
        "nodemanager": [8042, 8040]
    },
    "spark": {
        "master": [8080, 7077],
        "worker": [8081],
        "history-server": [18080]
    },
    "hive": {
        "metastore": [9083],
        "hiveserver2": [10000, 10002]
    },
    "kafka": {
        "broker": [9092, 9093]
    },
    "zookeeper": {
        "server": [2181, 2888, 3888]
    },
    "flink": {
        "jobmanager": [8081],
        "taskmanager": [8082]
    }
}