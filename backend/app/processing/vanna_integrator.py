# from pathlib import Path
# import sqlite3
# from typing import Dict, Any
# import os
# import re
# import shutil
# from core.logger import logger

# # Use your custom subclass that combines ChromaDB vector store + Gemini chat
# from vanna.chromadb import ChromaDB_VectorStore
# from vanna.google import GoogleGeminiChat
# # PersistentClient to make Chroma auto‑persist into our folder
# from chromadb import PersistentClient
# from chromadb.config import Settings


# class MyVanna(ChromaDB_VectorStore, GoogleGeminiChat):
#     def __init__(self, config: Dict[str, Any] = None):
#         """
#         Wraps ChromaDB_VectorStore and GoogleGeminiChat, 
#         wiring a PersistentClient that writes directly to disk.
#         """
#         config = config or {}

#         chroma_path = config.get("chromadb_path")
#         if chroma_path:
#             # ensure a clean directory on init
#             # if os.path.exists(chroma_path):
#             #     shutil.rmtree(chroma_path)
#             os.makedirs(chroma_path, exist_ok=True)

#             # create a PersistentClient that writes to chroma_path
#             client = PersistentClient(path=chroma_path, settings=Settings())

#             # inject into the ChromaDB_VectorStore config
#             config["client"] = client
#             config["persist_directory"] = chroma_path

#         # initialize both bases
#         ChromaDB_VectorStore.__init__(self, config=config)
#         GoogleGeminiChat.__init__(self, config=config)


class VannaIntegrator:
    def __init__(self, config):
        self.config = config

    def query(self, prompt):
        return f"Mocked response for prompt: {prompt}"

# class VannaIntegrator:
#     """Handles integration with Vanna AI for different database types using MyVanna."""
#     def __init__(self, config: Dict[str, Any]):
#         # config should include api_key and Gemini model
#         self.vanna_config = config
#         self._instance = {}  # Dictionary to store instances per chatbot_id
#         # Set base storage directory
#         self.storage_base_dir = config.get("storage_base_dir", "db_storage")

#     def get_instance(self, chatbot_id: str):
#         """Get or create a Vanna instance for a specific chatbot"""
        
#         # Validate it's actually a MongoDB ObjectId
#         if not re.match(r'^[0-9a-f]{24}$', chatbot_id):
#             raise ValueError(f"Invalid ObjectId format: {chatbot_id}")
            
#         if chatbot_id not in self._instance:
#             # Continue with the rest of your original code
#             chatbot_config = self.vanna_config.copy()
#             chatbot_dir = os.path.join(self.storage_base_dir, chatbot_id)
#             os.makedirs(chatbot_dir, exist_ok=True)
            
#             chatbot_config["chromadb_path"] = chatbot_dir
            
#             vn = MyVanna(config=chatbot_config)
#             self._instance[chatbot_id] = vn
            
#             logger.info(f"Created Vanna instance for chatbot {chatbot_id} with storage at {chatbot_dir}")
        
#         return self._instance[chatbot_id]
            


#     def process_sqlite(self, config: Dict[str, Any]) -> Dict[str, Any]:
#         result = {"status": "success"}
#         db_path = config.get("db_path")
#         model = config.get("vanna_model")
#         try:
#             # Connect to SQLite database
#             # self.vn.connect_to_sqlite(db_path)
            
#             # Set the model
#             # if model:
#             #     self.vn.set_model(model)
                
#             # Train on first table
#             conn = sqlite3.connect(db_path)
#             cursor = conn.cursor()
#             cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;")
#             table = cursor.fetchone()
#             if table:
#                 # Train the model
#                 self.vn.train(f"SELECT * FROM {table[0]};")
#                 result["trained_on"] = table[0]
#             conn.close()
#         except Exception as e:
#             result = {"status": "error", "message": str(e)}
#         return result

#     def train_sqlite(self, config: Dict[str, Any], chatbot_id: str = None) -> Dict[str, Any]:
#             """
#             Train the model on all table definitions in a SQLite database.
            
#             Args:
#                 config: Configuration dictionary containing db_path
#                 chatbot_id: Optional ID of the chatbot to train
                
#             Returns:
#                 Dictionary with status and any error messages
#             """
#             result = {"status": "success"}
#             try:
#                 # Get the vanna instance for this chatbot
#                 vn = self.get_instance(chatbot_id) if chatbot_id else MyVanna(config=self.vanna_config)
                
#                 # Make sure we're connected to SQLite first
#                 if config.get("db_type") == "sqlite":
#                     # Connect to the database if not already connected
#                     connection_result = self.connect_to_database(config, chatbot_id)
#                     if connection_result["status"] == "error":
#                         return connection_result
                
#                 # Get all table definitions
#                 logger.info("Fetching table definitions for training")
#                 df_ddl = vn.run_sql("SELECT type, sql FROM sqlite_master WHERE sql is not null")
                
#                 # Train on each table definition
#                 logger.info(f"Training on {len(df_ddl)} table definitions")
#                 train_count = 0
#                 for ddl in df_ddl['sql'].to_list():
#                     if ddl:  # Ensure the DDL statement is not None or empty
#                         vn.train(ddl=ddl)
#                         train_count += 1
                
#                 # if hasattr(vn, "client"):
#                 #     vn.client.persist()
#                 # elif hasattr(vn, "_client"):
#                 #     vn._client.persist()
#                 # Add more detailed information to the result
#                 logger.info("Persisting Chroma database...")
#                 try:
#                     # Force persist the ChromaDB collection
#                     if hasattr(vn, "_collection"):
#                         vn._collection.persist()
#                     logger.info("ChromaDB collection persisted successfully")
#                     logger.info("ChromaDB collection persisted successfully")
#                 except Exception as e:
#                     logger.error(f"Error persisting ChromaDB: {e}")
#                 result["trained_on_count"] = train_count
#                 result["message"] = f"Successfully trained on {train_count} table definitions"
#                 logger.info(result["message"])
                
#             except Exception as e:
#                 error_msg = f"Error during SQLite training: {str(e)}"
#                 logger.error(error_msg)
#                 result = {"status": "error", "message": error_msg}
                
#             return result

#     def process_sql_dump(self, config: Dict[str, Any]) -> Dict[str, Any]:
#         result = {"status": "success"}
#         orig = Path(config.get("db_path"))
#         temp_db = orig.parent / "temp_import.sqlite"
#         try:
#             # Load dump into temp SQLite
#             conn = sqlite3.connect(temp_db)
#             sql = orig.read_text()
#             if config.get("db_type") == "postgres_dump":
#                 sql = sql.replace("SERIAL", "INTEGER")
#             conn.executescript(sql)
#             conn.close()
            
#             # Update config to point to processed DB
#             config["processed_db_path"] = str(temp_db)
            
#             # Connect to temp SQLite database
#             self.vn.connect_to_sqlite(str(temp_db))
            
#             # Set the model if provided
#             model = config.get("vanna_model")
#             if model:
#                 self.vn.set_model(model)
                
#             # Train on first table
#             conn = sqlite3.connect(temp_db)
#             cursor = conn.cursor()
#             cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;")
#             table = cursor.fetchone()
#             if table:
#                 self.vn.train(f"SELECT * FROM {table[0]};")
#                 result["trained_on"] = table[0]
#             conn.close()
#         except Exception as e:
#             result = {"status": "error", "message": str(e)}
#         return result

#     def connect_to_database(self, config: Dict[str, Any], chatbot_id: str = None) -> Dict[str, Any]:
#             """Connect to different database types based on config."""
#             result = {"status": "success"}
#             db_type = config.get("db_type", "unknown")
            
#             try:
#                 # Get the vanna instance for this chatbot
#                 vn = self.get_instance(chatbot_id) if chatbot_id else MyVanna(config=self.vanna_config)
                
#                 if db_type == "sqlite":
#                     vn.connect_to_sqlite(config.get("db_path"))
#                 elif db_type == "mysql":
#                     vn.connect_to_mysql(
#                         host=config.get("host"),
#                         dbname=config.get("dbname"),
#                         user=config.get("user"),
#                         password=config.get("password"),
#                         port=config.get("port")
#                     )
#                 elif db_type == "postgres":
#                     vn.connect_to_postgres(
#                         host=config.get("host"),
#                         dbname=config.get("dbname"),
#                         user=config.get("user"),
#                         password=config.get("password"),
#                         port=config.get("port")
#                     )
#                 elif db_type == "snowflake":
#                     vn.connect_to_snowflake(
#                         account=config.get("account"),
#                         user=config.get("user"),
#                         password=config.get("password"),
#                         database=config.get("database"),
#                         schema=config.get("schema"),
#                         warehouse=config.get("warehouse")
#                     )
#                 elif db_type == "bigquery":
#                     vn.connect_to_bigquery(
#                         project_id=config.get("project_id"),
#                         dataset_id=config.get("dataset_id")
#                     )
#                 else:
#                     return {"status": "error", "message": f"Unsupported database type: {db_type}"}
                    
                
                    
#                 # Store the instance if chatbot_id provided
#                 if chatbot_id:
#                     self._instance[chatbot_id] = vn
                    
#             except Exception as e:
#                 result = {"status": "error", "message": str(e)}
                
#             return result

#     def rebuild_kb(self, config: Dict[str, Any]) -> Dict[str, Any]:
#         """First connect to the database, then process it based on type."""
#         db_type = config.get("db_type", "unknown")
        
#         # First connect to the database
#         connection_result = self.connect_to_database(config)
#         logger.debug(f"Connection result {connection_result}")
#         if connection_result["status"] == "error":
#             return connection_result
            
#         # Then process specifically for each type
#         if db_type == "sqlite":
#             return self.process_sqlite(config)
#         elif db_type in ("sql_dump", "postgres_dump"):
#             return self.process_sql_dump(config)
#         else:
#             # For other db types, we've already connected above
#             return {"status": "success", "message": f"Connected to {db_type} database"}