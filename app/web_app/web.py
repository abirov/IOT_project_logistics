<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Package Registration</title>
</head>
<body>
    <h1>Register a New Package</h1>
    <form id="packageForm" action="http://127.0.0.1:8081/packages/packages" method="post">
        Name: <input type="text" id="name" name="name" required><br>
        Weight: <input type="number" id="weight" name="weight" step="0.01" required><br>
        Length: <input type="number" id="length" name="length" step="0.01" required><br>
        Width: <input type="number" id="width" name="width" step="0.01" required><br>
        Height: <input type="number" id="height" name="height" step="0.01" required><br>
        Warehouse ID: <input type="text" id="warehouse_id" name="warehouse_id" required><br>
        Status: <select id="status" name="status">
            <option value="in warehouse">In Warehouse</option>
            <option value="en route">En Route</option>
            <option value="delivered">Delivered</option>
        </select><br>
        <button type="submit">Submit</button>
    </form>

    <script>
        document.getElementById('packageForm').onsubmit = function(event) {
            event.preventDefault();  // Prevent the default form submission
            const formData = {
                name: document.getElementById('name').value,
                weight: parseFloat(document.getElementById('weight').value),
                dimensions: {
                    length: parseFloat(document.getElementById('length').value),
                    width: parseFloat(document.getElementById('width').value),
                    height: parseFloat(document.getElementById('height').value)
                },
                warehouse_id: document.getElementById('warehouse_id').value,
                status: document.getElementById('status').value
            };

            fetch(this.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => alert('Package registered successfully!'))
            .catch(error => alert('Error registering package: ' + error));
        };
    </script>
</body>
</html>
