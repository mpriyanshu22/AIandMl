import logging

logger = logging.getLogger(__name__)

# ❌ Bad (STDIO)
print("Processing request")

# ✅ Good (STDIO)
logger.info("Processing request")  # writes to stderr