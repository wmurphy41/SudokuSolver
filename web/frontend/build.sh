#!/bin/sh
# Build script for placeholder frontend
mkdir -p dist
cat > dist/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SudokuSolver</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        p {
            color: #666;
            line-height: 1.6;
        }
        .status {
            background: #e8f4fd;
            border: 1px solid #bee5eb;
            border-radius: 4px;
            padding: 15px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 SudokuSolver</h1>
        <p>Welcome to the SudokuSolver web application!</p>
        <div class="status">
            <strong>Status:</strong> Frontend scaffolding in progress<br>
            <strong>Backend:</strong> ✅ Ready<br>
            <strong>API:</strong> <a href="/api/healthz">/api/healthz</a>
        </div>
        <p>This is a placeholder page. The React frontend will be scaffolded next using Vite.</p>
    </div>
</body>
</html>
EOF
echo "Placeholder frontend built successfully"
