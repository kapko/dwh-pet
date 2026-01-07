  {{ config(materialized='table', schema='gold') }}                                                   
                                                                                                      
  select                                                                                              
      date(measured_at) as date,                                                                      
      avg(temperature) as avg_temp,                                                                   
      min(temperature) as min_temp,                                                                   
      max(temperature) as max_temp                                                                    
  from {{ ref('stg_weather') }}                                                                       
  group by 1                                                                                          
  order by 1      