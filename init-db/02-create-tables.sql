CREATE TABLE bronze.raw_weather ( 
      id SERIAL PRIMARY KEY,                      
      raw_data JSONB,                          
      loaded_at TIMESTAMP DEFAULT NOW()
);
