from mezzanine.conf import register_setting

register_setting(
    name="BLOG_USE_COMMENTS",
    description="Whether to allow comments on blog posts",
    label="Allow comments",
    editable=True,
    default=True,
)
