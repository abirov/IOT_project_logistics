**Driver Endpoints (/drivers)

  GET /drivers/list_all → List all drivers
  GET /drivers?driver_id=<id> → Get driver by ID
  GET /drivers?driver_name=<name> → Get driver by name
  GET /drivers?driver_id=<id>&reputation=true → Get driver reputation
  
    POST /drivers → Create a new driver
    
      PUT /drivers?driver_id=<id> → Update driver by ID
      PUT /drivers/reputation?driver_id=<id> → Update driver reputation
      
          DELETE /drivers?driver_id=<id> → Delete driver by ID
          
**Warehouse Endpoints (/warehouse)

  GET /warehouse/list_all → List all warehouses
  GET /warehouse?warehouse_id=<id> → Get warehouse by ID
  GET /warehouse?warehouse_id=<id>&reputation=true → Get warehouse reputation
  
    POST /warehouse → Create a new warehouse
    
      PUT /warehouse?warehouse_id=<id> → Update warehouse by ID
      
        DELETE /warehouse?warehouse_id=<id> → Delete warehouse by ID
**Vehicle Endpoints (/vehicle)

  GET /vehicle?vehicle_id=<id> → Get vehicle by ID
  GET /vehicle/list_all → List all vehicles (Bug: Code mistakenly calls list_all_drivers())
  
    POST /vehicle → Create a new vehicle
    
      PUT /vehicle?vehicle_id=<id> → Update vehicle by ID
      
        DELETE /vehicle?vehicle_id=<id> → Delete vehicle by ID
        
**Feedback Endpoints (/feedback)

  GET /feedback?feedback_id=<id> → Get feedback by ID
  GET /feedback?by_rating=<rating> → Get feedback by rating
  
    POST /feedback → Create feedback
    
      PUT /feedback?feedback_id=<id> → Update feedback by ID
      
        DELETE /feedback?feedback_id=<id> → Delete feedback by ID
