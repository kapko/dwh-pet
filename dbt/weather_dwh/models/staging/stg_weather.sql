 {{ config(materialized='view', schema='silver') }}                                                                                            
  select                                                                                              
      rw.id as source_id,                                                                             
      t.time_value::timestamp as measured_at,                                                         
      temp.temp_value::numeric as temperature,                                                        
      rw.loaded_at                                                                                    
  from {{ source('bronze', 'raw_weather') }} rw,                                                      
       jsonb_array_elements_text(rw.raw_data->'hourly'->'time') with ordinality as t(time_value, idx),
       jsonb_array_elements_text(rw.raw_data->'hourly'->'temperature_2m') with ordinality as temp(temp_value, temp_idx)
  where t.idx = temp.temp_idx  
