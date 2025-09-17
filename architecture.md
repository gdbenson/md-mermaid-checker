---
title: System Architecture
description: Technical architecture and design patterns for the MAMS migration system
---

# System Architecture

This page describes the technical architecture of the MAMS (Multi-Agent Migration System) and the recommended SnapLogic implementation patterns for the migrated jobs.

## MAMS System Architecture

### Multi-Agent System Design

```mermaid
graph TD
    A[Main Orchestrator Agent] --> B[job-discovery]
    A --> C[job-analyzer]
    A --> D[root-job-creation]
    A --> E[migration-planner]
    A --> F[slpy-generator]
    A --> G[test-data-generator]
    A --> H[ui-generator]

    B --> I[Platform Exports<br/>XML Files]
    C --> J[Individual Analysis<br/>Documents]
    D --> K[Root Job Families<br/>Structured Analysis]
    E --> L[Migration Guides<br/>SnapLogic Strategies]
    F --> M[SLPy Pipelines<br/>Production Code]
    G --> N[Test Data Suites<br/>Validation Assets]
    H --> O[Documentation Site<br/>Professional UI]

    style A fill:#e1f5fe
    style B fill:#e8f5e8
    style C fill:#e8f5e8
    style D fill:#e8f5e8
    style E fill:#fff3e0
    style F fill:#fff3e0
    style G fill:#fff3e0
    style H fill:#f3e5f5
```

### Agent Workflow Pattern

The MAMS system follows a structured 7-phase workflow:

1. **Discovery Phase**: Lightweight scanning of platform exports
2. **Analysis Phase**: Detailed individual job analysis (one at a time)
3. **Synthesis Phase**: Job family creation from individual analyses
4. **Planning Phase**: SnapLogic migration strategy development
5. **Generation Phase**: Production-ready SLPy code generation
6. **Testing Phase**: Comprehensive test data suite creation
7. **Documentation Phase**: Professional UI and documentation generation

### Context Management Strategy

```mermaid
flowchart LR
    A[Large XML Files<br/>Platform Exports] --> B[Lightweight Discovery<br/>Metadata Only]
    B --> C[Individual Processing<br/>One Job at a Time]
    C --> D[Progressive Building<br/>Incremental Analysis]
    D --> E[Comprehensive Synthesis<br/>Complete Families]
    E --> F[Migration Assets<br/>Production Ready]

    style A fill:#ffcccc
    style B fill:#e8f5e8
    style C fill:#e8f5e8
    style D fill:#e8f5e8
    style E fill:#e8f5e8
    style F fill:#e1f5fe
```

## SnapLogic Migration Architecture

### Overall Migration Strategy

The migration follows a **Hybrid Orchestration** approach, combining orchestration redesign with component modernization:

- **Ultra Tasks** for complex orchestration and routing
- **Pipeline Execute** patterns for sequential workflow control
- **Specialized Pipelines** for focused data processing tasks
- **Error Handling Frameworks** for comprehensive monitoring

### Bloomberg AUDNZD Architecture

```mermaid
graph TD
    A[Main Pipeline<br/>SEQ_BloombergAUDNZD_To_S3] --> B[Bloomberg API Pipeline<br/>Data Retrieval]
    A --> C[File Decryption Pipeline<br/>Script Execution]
    A --> D[Data Processing Pipeline<br/>Row Filtering 44-73]
    A --> E[S3 Upload Pipeline 1<br/>Bloomberg_Rates/]
    A --> F[S3 Upload Pipeline 2<br/>source/bloomberg/]
    A --> G[File Management Pipeline<br/>Archive & Cleanup]
    A --> H[Error Handling Pipeline<br/>Email Notifications]

    B --> I[HTTP Client Snap<br/>Bloomberg API]
    C --> J[Script Snap<br/>decrypt_audnzd.sh]
    D --> K[File Reader + Mapper<br/>+ Filter Snaps]
    E --> L[S3 File Writer<br/>Primary Path]
    F --> M[S3 File Writer<br/>Secondary Path]
    G --> N[Script Snap<br/>File Operations]
    H --> O[Email Snap<br/>SMTP Notifications]

    style A fill:#e1f5fe
    style H fill:#ffcccc
```

#### Bloomberg Technical Stack
| Component | DataStage Original | SnapLogic Implementation |
|-----------|-------------------|-------------------------|
| **Orchestration** | Sequence Job | Pipeline Execute Pattern |
| **API Integration** | Response_File job | HTTP Client Snap |
| **File Decryption** | Shell script (decrypt_audnzd.sh) | Script Snap |
| **Data Filtering** | Row filter transformer | Filter Snap (rows 44-73) |
| **S3 Upload** | External job calls | S3 File Writer Snaps |
| **Error Handling** | DSSendMail | Email Snap |
| **File Management** | DSU.ExecSH | Script Snap |

### INSPECTIONS CDC Architecture

```mermaid
graph TD
    A[Main Ultra Task<br/>INSPECTIONS_CDC_Controller] --> B{Obfuscation Router<br/>Parameter-based}
    B -->|Standard| C[Standard CDC Ultra Task<br/>Normal Processing]
    B -->|Obfuscated| D[Privacy CDC Ultra Task<br/>Obfuscation Enabled]

    C --> E[Snowflake Extract<br/>Standard Data]
    D --> F[Snowflake Extract<br/>+ Obfuscation Layer]

    E --> G[CDC Processing<br/>Change Detection]
    F --> G

    G --> H[Delta S3 Upload<br/>JSONL with Operations]
    G --> I[Full S3 Upload<br/>Complete Dataset]

    C --> J[File Management<br/>Archive & Cleanup]
    D --> J

    A --> K[Error Handling<br/>Email & Monitoring]

    style A fill:#e1f5fe
    style B fill:#fff3e0
    style D fill:#ffcccc
    style K fill:#ffcccc
```

#### INSPECTIONS Technical Stack
| Component | DataStage Original | SnapLogic Implementation |
|-----------|-------------------|-------------------------|
| **Main Controller** | SEQ_INSPECTIONS_CDC_MSTR_MAIN | Ultra Task with routing |
| **CDC Orchestration** | 2 sequence jobs | 2 Ultra Tasks (standard/privacy) |
| **Data Extraction** | 2 parallel jobs | Snowflake Select Snaps |
| **Data Obfuscation** | Transformer stages | Advanced Mapper expressions |
| **Change Detection** | File comparison job | SCD/Diff Snap patterns |
| **S3 Upload** | 2 parallel jobs | S3 File Writer Snaps |
| **JSONL Conversion** | Column export | JSON Formatter Snap |
| **File Management** | DSU.ExecSH | Script Snap |

## Data Architecture Patterns

### Source-to-Target Mapping

#### Bloomberg Data Flow
```mermaid
flowchart LR
    A[Bloomberg API<br/>External Service] --> B[Encrypted Response<br/>blmbrg_rate_audnzd.out]
    B --> C[Decryption Process<br/>decrypt_audnzd.sh]
    C --> D[Raw Rate Data<br/>blmbrg_rate_audnzd.txt]
    D --> E[Data Filtering<br/>Rows 44-73 Extract]
    E --> F[Processed Rates<br/>blmbrg_audnzd_final.txt]
    F --> G[Dual S3 Upload<br/>Two Paths]
    G --> H[S3: Bloomberg_Rates/<br/>Primary Target]
    G --> I[S3: source/bloomberg/<br/>Secondary Target]
    F --> J[Archive<br/>Timestamped Storage]
```

#### INSPECTIONS Data Flow
```mermaid
flowchart LR
    A[Snowflake CWMS<br/>PUBLIC.INSPECTIONS] --> B{Obfuscation<br/>Decision}
    B -->|Standard| C[Standard Extract<br/>19 Fields]
    B -->|Privacy| D[Obfuscated Extract<br/>Character Replacement]

    C --> E[CDC Processing<br/>Change Detection]
    D --> E

    E --> F[Delta Changes<br/>INSERT/UPDATE/DELETE]
    E --> G[Full Dataset<br/>Complete Records]

    F --> H[Delta S3 Upload<br/>JSONL with Operations]
    G --> I[Full S3 Upload<br/>JSONL Complete]

    H --> J[S3: .INSPECTIONS_ct/<br/>Delta Path]
    I --> K[S3: .INSPECTIONS/<br/>Full Path]

    C --> L[Archive Management<br/>File Lifecycle]
    D --> L
```

### Parameter Architecture

#### Parameter Flow Patterns
```mermaid
graph TD
    A[Environment Parameters<br/>$PROJDEF Values] --> B[Job Family Parameters<br/>Root Job Sets]
    B --> C[Sub-Job Parameters<br/>Inherited Values]
    C --> D[Snap Configuration<br/>Runtime Values]

    A --> E[Connection Parameters<br/>Database/API Credentials]
    A --> F[System Parameters<br/>File Paths, Grid Config]
    A --> G[Business Parameters<br/>Processing Flags]

    E --> H[Account Settings<br/>SnapLogic Connections]
    F --> I[Snaplex Configuration<br/>Resource Allocation]
    G --> J[Pipeline Parameters<br/>Business Logic Control]

    style A fill:#e1f5fe
    style H fill:#e8f5e8
    style I fill:#e8f5e8
    style J fill:#fff3e0
```

#### Key Parameter Mappings
| DataStage Parameter | SnapLogic Equivalent | Purpose |
|-------------------|---------------------|---------|
| `ps_Bloomberg` | Account Connection | Bloomberg API credentials |
| `CWMS_SF_Azure` | Account Connection | Snowflake database connection |
| `$APT_CONFIG_FILE` | Snaplex Configuration | Parallel processing setup |
| `$Enterprise_Path` | Pipeline Parameter | File system base path |
| `$Helios_S3_*` | Account Connection | S3 storage credentials |
| `$EmailServer` | Account Connection | SMTP notification server |
| `Delta` | Pipeline Parameter | Processing mode flag |
| `Obfuscation_IND` | Pipeline Parameter | Privacy processing flag |

## Security Architecture

### Security Implementation Patterns

#### Data Protection Strategy
```mermaid
graph TD
    A[Source Data<br/>Production Systems] --> B[Encryption in Transit<br/>TLS/SSL]
    B --> C[SnapLogic Processing<br/>Secure Snaplex]
    C --> D[Data Obfuscation<br/>Privacy Layer]
    D --> E[Encryption at Rest<br/>S3 Server-side]
    E --> F[Target Systems<br/>Secure Storage]

    G[Access Control<br/>RBAC] --> C
    H[Audit Logging<br/>Data Lineage] --> C
    I[Key Management<br/>Credential Vault] --> C

    style D fill:#ffcccc
    style G fill:#fff3e0
    style H fill:#fff3e0
    style I fill:#fff3e0
```

#### Security Controls by Component
| Component | DataStage Security | SnapLogic Security | Enhancement |
|-----------|-------------------|-------------------|-------------|
| **API Access** | Parameter sets | Account credentials | Encrypted vault storage |
| **Database** | Connection strings | Account connections | Certificate-based auth |
| **File Encryption** | Shell script | Script snap + vault | Centralized key management |
| **Data Obfuscation** | Transform stages | Expression library | Configurable patterns |
| **S3 Upload** | AWS keys in params | Account credentials | IAM role-based access |
| **Audit Trail** | Job logs | Pipeline monitoring | Enhanced data lineage |

## Performance Architecture

### Scalability Patterns

#### Resource Allocation Strategy
```mermaid
graph TD
    A[Snaplex Cluster<br/>Compute Resources] --> B[Load Balancer<br/>Work Distribution]
    B --> C[Bloomberg Pipelines<br/>2-3 Nodes]
    B --> D[INSPECTIONS Pipelines<br/>4-6 Nodes]

    E[Connection Pooling<br/>Database Efficiency] --> F[Snowflake Connections<br/>Optimized Queries]
    E --> G[S3 Connections<br/>Parallel Uploads]

    H[Memory Management<br/>Data Streaming] --> I[Large Dataset Processing<br/>2M+ Records]
    H --> J[File Processing<br/>Efficient I/O]

    style A fill:#e1f5fe
    style E fill:#e8f5e8
    style H fill:#fff3e0
```

#### Performance Optimization Features
| Optimization Area | Bloomberg | INSPECTIONS | Implementation |
|------------------|-----------|-------------|----------------|
| **Parallel Processing** | API calls, dual S3 uploads | Snowflake pagination, CDC processing | Multiple pipeline instances |
| **Memory Management** | Stream processing | Large dataset streaming | Efficient data structures |
| **Connection Pooling** | HTTP/S3 connections | Snowflake/S3 connections | Shared connection pools |
| **Batch Processing** | File-based batching | Record-level batching | Configurable batch sizes |
| **Error Recovery** | Checkpoint/restart | Transaction boundaries | Ultra Task state management |

## Monitoring and Observability

### Monitoring Architecture
```mermaid
graph TD
    A[SnapLogic Manager<br/>Central Monitoring] --> B[Pipeline Execution<br/>Runtime Metrics]
    B --> C[Performance Metrics<br/>Throughput, Latency]
    B --> D[Error Tracking<br/>Exception Handling]
    B --> E[Data Quality<br/>Validation Results]

    F[External Monitoring<br/>Enterprise Tools] --> A
    G[Alerting System<br/>Email/SMS] --> A
    H[Audit Logging<br/>Compliance Trail] --> A

    I[Custom Dashboards<br/>Business Metrics] --> A
    J[SLA Monitoring<br/>Performance Targets] --> A

    style A fill:#e1f5fe
    style D fill:#ffcccc
    style G fill:#fff3e0
```

### Key Monitoring Metrics
| Metric Category | Bloomberg KPIs | INSPECTIONS KPIs | Threshold |
|-----------------|----------------|------------------|-----------|
| **Execution Time** | < 5 minutes | < 30 minutes | SLA compliance |
| **Data Volume** | ~1K records/day | 2M+ records/run | Volume validation |
| **Success Rate** | > 99.9% | > 99.5% | Error rate monitoring |
| **Data Quality** | 100% rate accuracy | 100% CDC accuracy | Quality validation |
| **Security Events** | Encryption success | Obfuscation compliance | Security monitoring |

## Deployment Architecture

### Environment Strategy
```mermaid
graph TD
    A[Development Environment<br/>Pipeline Development] --> B[Testing Environment<br/>Integration Testing]
    B --> C[Staging Environment<br/>Pre-production Validation]
    C --> D[Production Environment<br/>Live Processing]

    E[Source Control<br/>Version Management] --> A
    F[CI/CD Pipeline<br/>Automated Deployment] --> B
    G[Configuration Management<br/>Environment-specific] --> C
    H[Monitoring & Alerting<br/>Production Support] --> D

    style A fill:#e8f5e8
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#e1f5fe
```

### Deployment Considerations
| Environment | Bloomberg Setup | INSPECTIONS Setup | Requirements |
|-------------|----------------|-------------------|--------------|
| **Development** | Sandbox API, Mock S3 | Test Snowflake, Mock S3 | Pipeline development |
| **Testing** | Production API, Test S3 | Staging Snowflake, Test S3 | End-to-end validation |
| **Staging** | Production API, Staging S3 | Production Snowflake, Staging S3 | Pre-production testing |
| **Production** | Live API, Production S3 | Production Snowflake, Live S3 | Business operations |

This architecture provides a robust, scalable, and secure foundation for migrating the DataStage jobs to SnapLogic while maintaining performance, security, and operational requirements.