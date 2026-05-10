-- DocMind 数据库初始化
ALTER DATABASE CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 性能索引（补充 SQLAlchemy 自动创建的索引）
CREATE INDEX IF NOT EXISTS ix_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS ix_chat_sessions_organization_id ON chat_sessions(organization_id);
CREATE INDEX IF NOT EXISTS ix_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS ix_documents_organization_id ON documents(organization_id);
CREATE INDEX IF NOT EXISTS ix_documents_uploaded_by ON documents(uploaded_by);
CREATE INDEX IF NOT EXISTS ix_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS ix_document_chunks_document_id ON document_chunks(document_id);
