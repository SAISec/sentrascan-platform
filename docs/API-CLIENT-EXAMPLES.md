# API Client Examples

Code examples for integrating with SentraScan Platform API.

## Table of Contents

1. [Python Client](#python-client)
2. [JavaScript/TypeScript Client](#javascripttypescript-client)
3. [cURL Examples](#curl-examples)
4. [Go Client](#go-client)
5. [Ruby Client](#ruby-client)

---

## Python Client

### Basic Client

```python
import requests
from typing import Optional, List, Dict

class SentraScanClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def health(self) -> Dict:
        """Check API health"""
        response = requests.get(f"{self.base_url}/api/v1/health")
        response.raise_for_status()
        return response.json()
    
    def scan_mcp(self, 
                 auto_discover: bool = True,
                 config_paths: Optional[List[str]] = None,
                 policy: Optional[str] = None,
                 timeout: int = 60) -> Dict:
        """Scan MCP configurations"""
        payload = {
            "auto_discover": auto_discover,
            "timeout": timeout
        }
        if config_paths:
            payload["config_paths"] = config_paths
        if policy:
            payload["policy"] = policy
        
        response = requests.post(
            f"{self.base_url}/api/v1/mcp/scans",
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def scan_model(self,
                   paths: List[str],
                   generate_sbom: bool = False,
                   strict: bool = False,
                   policy: Optional[str] = None) -> Dict:
        """Scan ML model"""
        payload = {
            "paths": paths,
            "generate_sbom": generate_sbom,
            "strict": strict
        }
        if policy:
            payload["policy"] = policy
        
        response = requests.post(
            f"{self.base_url}/api/v1/models/scans",
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_scan(self, scan_id: str) -> Dict:
        """Get scan details"""
        response = requests.get(
            f"{self.base_url}/api/v1/scans/{scan_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def list_scans(self, 
                   scan_type: Optional[str] = None,
                   passed: Optional[bool] = None,
                   limit: int = 50,
                   offset: int = 0) -> List[Dict]:
        """List scans"""
        params = {"limit": limit, "offset": offset}
        if scan_type:
            params["type"] = scan_type
        if passed is not None:
            params["passed"] = str(passed).lower()
        
        response = requests.get(
            f"{self.base_url}/api/v1/scans",
            params=params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Usage
client = SentraScanClient(
    base_url="http://localhost:8200",
    api_key="your-api-key"
)

# Scan MCP
result = client.scan_mcp(auto_discover=True)
if result["gate_result"]["passed"]:
    print("✅ Scan passed")
else:
    print(f"❌ Scan failed: {result['gate_result']['total_findings']} findings")

# Scan model
result = client.scan_model(
    paths=["model.pkl"],
    generate_sbom=True
)
```

### Async Client

```python
import aiohttp
import asyncio

class AsyncSentraScanClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    async def scan_mcp(self, auto_discover: bool = True) -> Dict:
        """Scan MCP configurations asynchronously"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/v1/mcp/scans",
                json={"auto_discover": auto_discover},
                headers=self.headers
            ) as response:
                response.raise_for_status()
                return await response.json()

# Usage
async def main():
    client = AsyncSentraScanClient(
        base_url="http://localhost:8200",
        api_key="your-api-key"
    )
    result = await client.scan_mcp()
    print(result)

asyncio.run(main())
```

---

## JavaScript/TypeScript Client

### TypeScript Client

```typescript
interface ScanResult {
  scan_id: string;
  timestamp: string;
  gate_result: {
    passed: boolean;
    total_findings: number;
    blocking_findings: number;
    critical_count: number;
    high_count: number;
  };
  findings: Finding[];
  metadata: {
    scan_duration_ms: number;
    servers_scanned?: number;
    engines_used?: string[];
  };
}

interface Finding {
  id: string;
  scanner: string;
  severity: string;
  category: string;
  title: string;
  description: string;
  location?: string;
  evidence?: any;
  remediation?: string;
}

class SentraScanClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string, apiKey: string) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.apiKey = apiKey;
  }

  private async request<T>(
    method: string,
    endpoint: string,
    body?: any
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method,
      headers: {
        'X-API-Key': this.apiKey,
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  async health(): Promise<{ status: string }> {
    return this.request('GET', '/api/v1/health');
  }

  async scanMCP(options: {
    autoDiscover?: boolean;
    configPaths?: string[];
    policy?: string;
    timeout?: number;
  }): Promise<ScanResult> {
    return this.request<ScanResult>('POST', '/api/v1/mcp/scans', {
      auto_discover: options.autoDiscover ?? true,
      config_paths: options.configPaths,
      policy: options.policy,
      timeout: options.timeout ?? 60,
    });
  }

  async scanModel(options: {
    paths: string[];
    generateSbom?: boolean;
    strict?: boolean;
    policy?: string;
  }): Promise<ScanResult> {
    return this.request<ScanResult>('POST', '/api/v1/models/scans', {
      paths: options.paths,
      generate_sbom: options.generateSbom ?? false,
      strict: options.strict ?? false,
      policy: options.policy,
    });
  }

  async getScan(scanId: string): Promise<ScanResult> {
    return this.request<ScanResult>('GET', `/api/v1/scans/${scanId}`);
  }

  async listScans(options: {
    type?: 'mcp' | 'model';
    passed?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<ScanResult[]> {
    const params = new URLSearchParams();
    if (options.type) params.append('type', options.type);
    if (options.passed !== undefined) params.append('passed', String(options.passed));
    if (options.limit) params.append('limit', String(options.limit));
    if (options.offset) params.append('offset', String(options.offset));

    return this.request<ScanResult[]>(
      'GET',
      `/api/v1/scans?${params.toString()}`
    );
  }
}

// Usage
const client = new SentraScanClient(
  'http://localhost:8200',
  'your-api-key'
);

// Scan MCP
const result = await client.scanMCP({ autoDiscover: true });
if (result.gate_result.passed) {
  console.log('✅ Scan passed');
} else {
  console.log(`❌ Scan failed: ${result.gate_result.total_findings} findings`);
}
```

### Node.js Example

```javascript
const axios = require('axios');

class SentraScanClient {
  constructor(baseUrl, apiKey) {
    this.client = axios.create({
      baseURL: baseUrl,
      headers: {
        'X-API-Key': apiKey,
        'Content-Type': 'application/json',
      },
    });
  }

  async scanMCP(autoDiscover = true) {
    const response = await this.client.post('/api/v1/mcp/scans', {
      auto_discover: autoDiscover,
    });
    return response.data;
  }

  async scanModel(paths, options = {}) {
    const response = await this.client.post('/api/v1/models/scans', {
      paths,
      generate_sbom: options.generateSbom || false,
      strict: options.strict || false,
    });
    return response.data;
  }
}

// Usage
const client = new SentraScanClient(
  'http://localhost:8200',
  'your-api-key'
);

client.scanMCP(true).then(result => {
  console.log(result);
});
```

---

## cURL Examples

### Health Check

```bash
curl http://localhost:8200/api/v1/health
```

### MCP Scan

```bash
curl -X POST http://localhost:8200/api/v1/mcp/scans \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "auto_discover": true
  }'
```

### Model Scan

```bash
curl -X POST http://localhost:8200/api/v1/models/scans \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "paths": ["model.pkl"],
    "generate_sbom": true
  }'
```

### Get Scan

```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8200/api/v1/scans/scan-id
```

### List Scans

```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8200/api/v1/scans?type=mcp&limit=10"
```

### Create Baseline

```bash
curl -X POST http://localhost:8200/api/v1/baselines \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "baseline_type": "mcp",
    "name": "production-baseline",
    "content": {...}
  }'
```

---

## Go Client

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
)

type SentraScanClient struct {
    BaseURL string
    APIKey  string
}

type ScanResult struct {
    ScanID    string `json:"scan_id"`
    Timestamp string `json:"timestamp"`
    GateResult struct {
        Passed          bool `json:"passed"`
        TotalFindings   int  `json:"total_findings"`
        BlockingFindings int `json:"blocking_findings"`
    } `json:"gate_result"`
}

func (c *SentraScanClient) ScanMCP(autoDiscover bool) (*ScanResult, error) {
    payload := map[string]interface{}{
        "auto_discover": autoDiscover,
    }
    
    jsonData, err := json.Marshal(payload)
    if err != nil {
        return nil, err
    }
    
    req, err := http.NewRequest("POST", c.BaseURL+"/api/v1/mcp/scans", bytes.NewBuffer(jsonData))
    if err != nil {
        return nil, err
    }
    
    req.Header.Set("X-API-Key", c.APIKey)
    req.Header.Set("Content-Type", "application/json")
    
    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, err
    }
    
    var result ScanResult
    if err := json.Unmarshal(body, &result); err != nil {
        return nil, err
    }
    
    return &result, nil
}

func main() {
    client := &SentraScanClient{
        BaseURL: "http://localhost:8200",
        APIKey:  "your-api-key",
    }
    
    result, err := client.ScanMCP(true)
    if err != nil {
        panic(err)
    }
    
    if result.GateResult.Passed {
        fmt.Println("✅ Scan passed")
    } else {
        fmt.Printf("❌ Scan failed: %d findings\n", result.GateResult.TotalFindings)
    }
}
```

---

## Ruby Client

```ruby
require 'net/http'
require 'json'
require 'uri'

class SentraScanClient
  def initialize(base_url, api_key)
    @base_url = base_url
    @api_key = api_key
  end

  def scan_mcp(auto_discover: true)
    uri = URI("#{@base_url}/api/v1/mcp/scans")
    http = Net::HTTP.new(uri.host, uri.port)
    
    request = Net::HTTP::Post.new(uri.path)
    request['X-API-Key'] = @api_key
    request['Content-Type'] = 'application/json'
    request.body = {
      auto_discover: auto_discover
    }.to_json
    
    response = http.request(request)
    JSON.parse(response.body)
  end

  def scan_model(paths, generate_sbom: false)
    uri = URI("#{@base_url}/api/v1/models/scans")
    http = Net::HTTP.new(uri.host, uri.port)
    
    request = Net::HTTP::Post.new(uri.path)
    request['X-API-Key'] = @api_key
    request['Content-Type'] = 'application/json'
    request.body = {
      paths: paths,
      generate_sbom: generate_sbom
    }.to_json
    
    response = http.request(request)
    JSON.parse(response.body)
  end
end

# Usage
client = SentraScanClient.new('http://localhost:8200', 'your-api-key')
result = client.scan_mcp(auto_discover: true)

if result['gate_result']['passed']
  puts '✅ Scan passed'
else
  puts "❌ Scan failed: #{result['gate_result']['total_findings']} findings"
end
```

---

## Error Handling

### Python

```python
import requests
from requests.exceptions import RequestException

try:
    response = client.scan_mcp()
except RequestException as e:
    if e.response:
        if e.response.status_code == 401:
            print("Authentication failed")
        elif e.response.status_code == 403:
            print("Insufficient permissions")
        else:
            print(f"API error: {e.response.status_code}")
    else:
        print(f"Network error: {e}")
```

### JavaScript

```typescript
try {
  const result = await client.scanMCP();
} catch (error) {
  if (error.response) {
    if (error.response.status === 401) {
      console.error('Authentication failed');
    } else if (error.response.status === 403) {
      console.error('Insufficient permissions');
    } else {
      console.error(`API error: ${error.response.status}`);
    }
  } else {
    console.error(`Network error: ${error.message}`);
  }
}
```

---

## Next Steps

**Integration:**
- [CI/CD Integration](INTEGRATION-CICD.md) - Pipeline integration examples
- [User Guide](USER-GUIDE.md) - Complete usage guide

**Reference:**
- [Technical Documentation](TECHNICAL-DOCUMENTATION.md#api-documentation) - Complete API reference
- [Documentation Index](README.md) - Complete documentation overview

---

**API Support:** [Your API support contact]

