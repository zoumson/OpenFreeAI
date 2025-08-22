## 1. Linux / macOS Setup: Set `OPENAI_API_KEY` Environment Variable using zsh

### Step 1: Add the API key to your `.zshrc`

Replace `yourkey` with your actual OpenAI API key:

```bash
echo "export OPENAI_API_KEY='yourkey'" >> ~/.zshrc
```

### Step 2: Update the shell with the new variable

Apply the changes to your current terminal session:

```bash
source ~/.zshrc
```

### Step 3: Confirm that the environment variable is set

Check that your environment variable is properly set by running:

```bash
echo $OPENAI_API_KEY
```

### Step 4: Confirm api key does not have trailing new line

```bash
echo -n "$OPENAI_API_KEY" | od -c
```

### Step 5: Unset the current variable

```bash
unset OPENAI_API_KEY
```

### Step 6: Set it again without any trailing newline (replace your_actual_key with your real key):

```bash
export OPENAI_API_KEY='your_actual_key'
```

### Step 7: Verify it’s set without newline

```bash
echo -n "$OPENAI_API_KEY" | od -c
```

You should see just the key characters, no `\n`

## 2. Virtual environment

### Step 1: Create a virtual environment

```bash
python3 -m venv venv
```

### Step 2: Activate the virtual environment

```bash
source venv/bin/activate
```

(you’ll see (venv) appear in your terminal prompt)

### Step 3: Deactivate the virtual environment

```bash
deactivate
```
