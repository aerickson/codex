/// The current Codex CLI version as embedded at compile time.
pub const CODEX_CLI_VERSION: &str = match option_env!("CODEX_AJE_VERSION") {
    Some(version) => version,
    None => env!("CARGO_PKG_VERSION"),
};

/// Return the release baseline used when checking whether an AJE build is stale.
#[cfg(not(debug_assertions))]
pub(crate) fn update_check_version() -> &'static str {
    option_env!("CODEX_AJE_VERSION")
        .and_then(|version| version.split_once("-aje").map(|(release, _)| release))
        .unwrap_or(CODEX_CLI_VERSION)
}
