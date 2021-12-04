detect-secrets scan --no-keyword-scan > .secrets.baseline
detect-secrets audit .secrets.baseline

FILENAME=manifest.yml
while true; do
    read -p "Do you want to run the following command to remove the file $FILENAME from all history commits" yn
    case $yn in
        [Yy]* ) git filter-branch --force --index-filter "git rm --cached --ignore-unmatch $FILENAME"  --prune-empty --tag-name-filter cat -- --all; break;;
        [Nn]* )  exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

