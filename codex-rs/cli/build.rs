fn main() {
    println!("cargo:rerun-if-env-changed=CODEX_BUILD_VERSION");
    println!(
        "cargo:rustc-env=CODEX_BUILD_VERSION={}",
        std::env::var("CODEX_BUILD_VERSION").unwrap_or_else(|_| git_build_version())
    );

    if std::env::var("CARGO_CFG_TARGET_OS").as_deref() == Ok("macos") {
        println!("cargo:rustc-link-arg=-ObjC");
    }
}

fn git_build_version() -> String {
    let manifest_dir = std::env::var_os("CARGO_MANIFEST_DIR");
    let Some(manifest_dir) = manifest_dir else {
        return "0.0.0+unknown".to_string();
    };

    let sha = git(&manifest_dir, &["rev-parse", "--short=12", "HEAD"])
        .unwrap_or_else(|| "unknown".to_string());
    let dirty = git(
        &manifest_dir,
        ["status", "--porcelain", "--untracked-files=no"].as_slice(),
    )
    .is_some_and(|status| !status.is_empty());

    if dirty {
        format!("0.0.0+g{sha}.dirty")
    } else {
        format!("0.0.0+g{sha}")
    }
}

fn git(manifest_dir: &std::ffi::OsStr, args: &[&str]) -> Option<String> {
    let output = std::process::Command::new("git")
        .args(["-C", manifest_dir.to_str()?])
        .args(args)
        .output()
        .ok()?;
    output
        .status
        .success()
        .then(|| String::from_utf8_lossy(&output.stdout).trim().to_string())
}
