-- Transaction Trigger for Automatic Holdings Update
-- This trigger automatically updates the Holdings table when a transaction is recorded

-- Drop existing trigger and function if they exist
DROP TRIGGER IF EXISTS update_holdings_on_transaction ON transaction;
DROP FUNCTION IF EXISTS process_transaction_holdings();

-- Create the trigger function
CREATE OR REPLACE FUNCTION process_transaction_holdings()
RETURNS TRIGGER AS $$
DECLARE
    v_portfolio_id VARCHAR(10);
    v_current_holding_count INTEGER;
    v_current_average_price NUMERIC(10, 2);
    v_new_average_price NUMERIC(10, 2);
BEGIN
    -- Find the investor's portfolio (using the most recent one)
    SELECT portfolio_id INTO v_portfolio_id
    FROM portfolio
    WHERE investor_id = NEW.investor_id
    ORDER BY creation_date DESC
    LIMIT 1;
    
    -- If no portfolio exists for this investor, raise an error
    IF v_portfolio_id IS NULL THEN
        RAISE EXCEPTION 'No portfolio found for investor %', NEW.investor_id;
    END IF;
    
    -- Check if the holding already exists
    SELECT holding_count, average_price INTO v_current_holding_count, v_current_average_price
    FROM holdings
    WHERE stock_id = NEW.stock_id AND portfolio_id = v_portfolio_id;
    
    -- Process SELL transaction
    IF NEW.transaction_type = 'sell' THEN
        -- Check if holding exists
        IF v_current_holding_count IS NULL THEN
            RAISE EXCEPTION 'Cannot sell stock % - no holdings found in portfolio %', NEW.stock_id, v_portfolio_id;
        END IF;
        
        -- Check if there are enough shares to sell
        IF v_current_holding_count < NEW.unit_number THEN
            RAISE EXCEPTION 'Insufficient shares to sell. Available: %, Requested: %', v_current_holding_count, NEW.unit_number;
        END IF;
        
        -- Update holding: decrement holding_count
        UPDATE holdings
        SET holding_count = holding_count - NEW.unit_number
        WHERE stock_id = NEW.stock_id AND portfolio_id = v_portfolio_id;
        
        -- If holding_count becomes 0, delete the holding
        DELETE FROM holdings
        WHERE stock_id = NEW.stock_id 
          AND portfolio_id = v_portfolio_id 
          AND holding_count = 0;
        
        -- Update portfolio total_value (decrease by sale amount)
        UPDATE portfolio
        SET total_value = total_value - (NEW.unit_price * NEW.unit_number)
        WHERE portfolio_id = v_portfolio_id;
        
    -- Process BUY transaction
    ELSIF NEW.transaction_type = 'buy' THEN
        -- If holding exists, update it
        IF v_current_holding_count IS NOT NULL THEN
            -- Calculate new average price: (old_avg * old_count + new_price * new_count) / (old_count + new_count)
            v_new_average_price := (v_current_average_price * v_current_holding_count + NEW.unit_price * NEW.unit_number) 
                                   / (v_current_holding_count + NEW.unit_number);
            
            -- Update the holding
            UPDATE holdings
            SET holding_count = holding_count + NEW.unit_number,
                average_price = v_new_average_price
            WHERE stock_id = NEW.stock_id AND portfolio_id = v_portfolio_id;
        ELSE
            -- Create new holding
            INSERT INTO holdings (stock_id, portfolio_id, average_price, holding_count)
            VALUES (NEW.stock_id, v_portfolio_id, NEW.unit_price, NEW.unit_number);
        END IF;
        
        -- Update portfolio total_value (increase by purchase amount)
        UPDATE portfolio
        SET total_value = total_value + (NEW.unit_price * NEW.unit_number)
        WHERE portfolio_id = v_portfolio_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger
CREATE TRIGGER update_holdings_on_transaction
AFTER INSERT ON transaction
FOR EACH ROW
EXECUTE FUNCTION process_transaction_holdings();
