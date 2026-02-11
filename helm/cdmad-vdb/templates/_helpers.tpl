{{/*
Expand the name of the chart.
*/}}
{{- define "cdmad-vdb.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "cdmad-vdb.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Chart label value.
*/}}
{{- define "cdmad-vdb.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels.
*/}}
{{- define "cdmad-vdb.labels" -}}
helm.sh/chart: {{ include "cdmad-vdb.chart" . }}
{{ include "cdmad-vdb.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels.
*/}}
{{- define "cdmad-vdb.selectorLabels" -}}
app.kubernetes.io/name: {{ include "cdmad-vdb.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
ServiceAccount name.
*/}}
{{- define "cdmad-vdb.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "cdmad-vdb.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Resolved Postgres host (in-cluster service or external).
*/}}
{{- define "cdmad-vdb.postgresHost" -}}
{{- if .Values.postgres.enabled }}
{{- printf "%s-postgres" (include "cdmad-vdb.fullname" .) }}
{{- else }}
{{- required "externalDatabase.host is required when postgres.enabled=false" .Values.externalDatabase.host }}
{{- end }}
{{- end }}

{{/*
Resolved Postgres port.
*/}}
{{- define "cdmad-vdb.postgresPort" -}}
{{- if .Values.postgres.enabled }}
{{- "5432" }}
{{- else }}
{{- .Values.externalDatabase.port | toString }}
{{- end }}
{{- end }}

{{/*
Resolved Postgres database.
*/}}
{{- define "cdmad-vdb.postgresDatabase" -}}
{{- if .Values.postgres.enabled }}
{{- .Values.postgres.database }}
{{- else }}
{{- .Values.externalDatabase.database }}
{{- end }}
{{- end }}

{{/*
Resolved Postgres username.
*/}}
{{- define "cdmad-vdb.postgresUser" -}}
{{- if .Values.postgres.enabled }}
{{- .Values.postgres.username }}
{{- else }}
{{- .Values.externalDatabase.username }}
{{- end }}
{{- end }}

{{/*
Name of the Secret holding database credentials.
*/}}
{{- define "cdmad-vdb.secretName" -}}
{{- if and (not .Values.postgres.enabled) .Values.externalDatabase.existingSecret }}
{{- .Values.externalDatabase.existingSecret }}
{{- else }}
{{- include "cdmad-vdb.fullname" . }}
{{- end }}
{{- end }}

{{/*
Key in the Secret that holds the Postgres password.
*/}}
{{- define "cdmad-vdb.secretPasswordKey" -}}
{{- if and (not .Values.postgres.enabled) .Values.externalDatabase.existingSecret }}
{{- .Values.externalDatabase.existingSecretKey }}
{{- else }}
{{- "POSTGRES_PASSWORD" }}
{{- end }}
{{- end }}
